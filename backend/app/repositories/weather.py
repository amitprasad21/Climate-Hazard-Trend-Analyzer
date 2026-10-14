"""Normalized daily maxima per source key (docs/database.md, collection daily_weather)."""

from datetime import date, datetime, timedelta

from pymongo import ASCENDING, UpdateOne
from pymongo.asynchronous.database import AsyncDatabase

from app.ingestion import NORMALIZATION_VERSION, DailySeries, DailyValue
from app.repositories import ensure_collection, storage_errors
from app.schemas import SOURCE_PROFILES, ProviderName

COLLECTION = "daily_weather"
VALID_TTL = timedelta(days=30)
NEGATIVE_TTL = timedelta(hours=1)
NUMBER_OR_NULL = {"bsonType": ["double", "null"]}
VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "source_key",
            "provider",
            "date",
            "tmax_c",
            "quality",
            "duplicate_dates",
            "normalization_version",
            "retrieved_at",
            "expires_at",
        ],
        "properties": {
            "source_key": {"bsonType": "string"},
            "provider": {"enum": list(SOURCE_PROFILES)},
            "date": {"bsonType": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "tmax_c": NUMBER_OR_NULL,
            "quality": {"enum": ["valid", "missing", "invalid"]},
            "duplicate_dates": {"enum": [0, 1]},
            "requested_latitude": {"bsonType": "double"},
            "requested_longitude": {"bsonType": "double"},
            "resolved_latitude": NUMBER_OR_NULL,
            "resolved_longitude": NUMBER_OR_NULL,
            "elevation_m": NUMBER_OR_NULL,
            "retrieved_at": {"bsonType": "date"},
            "expires_at": {"bsonType": "date"},
        },
    }
}


def source_key(provider: ProviderName, latitude: float, longitude: float) -> str:
    model = SOURCE_PROFILES[provider].model
    parts = [provider, model, f"{latitude:.4f}", f"{longitude:.4f}", "UTC", "tmax_c"]
    return "|".join([*parts, NORMALIZATION_VERSION])


class WeatherRepository:
    def __init__(self, database: AsyncDatabase):
        self.database = database
        self.collection = database[COLLECTION]

    async def ensure_schema(self) -> None:
        await ensure_collection(self.database, COLLECTION, VALIDATOR)
        await self.collection.create_index(
            [("source_key", ASCENDING), ("date", ASCENDING)], unique=True, name="source_day"
        )
        await self.collection.create_index("expires_at", expireAfterSeconds=0, name="expiry")

    async def save(self, series: DailySeries) -> None:
        key = source_key(series.provider, *series.requested)
        resolved = series.resolved or (None, None)
        operations = [
            UpdateOne(
                {"source_key": key, "date": day.day.isoformat()},
                {
                    "$set": {
                        "provider": series.provider,
                        "requested_latitude": float(series.requested[0]),
                        "requested_longitude": float(series.requested[1]),
                        "resolved_latitude": resolved[0],
                        "resolved_longitude": resolved[1],
                        "elevation_m": series.elevation_m,
                        "tmax_c": day.tmax_c,
                        "quality": day.quality,
                        "duplicate_dates": int(day.duplicate),
                        "normalization_version": NORMALIZATION_VERSION,
                        "retrieved_at": series.retrieved_at,
                        "expires_at": series.retrieved_at
                        + (VALID_TTL if day.quality == "valid" else NEGATIVE_TTL),
                    }
                },
                upsert=True,
            )
            for day in series.days
        ]
        # One batch per calendar year keeps every write inside the per-operation timeout.
        by_year: dict[int, list[UpdateOne]] = {}
        for day, operation in zip(series.days, operations, strict=True):
            by_year.setdefault(day.day.year, []).append(operation)
        with storage_errors():
            for batch in by_year.values():
                await self.collection.bulk_write(batch, ordered=False)

    async def load(
        self,
        provider: ProviderName,
        latitude: float,
        longitude: float,
        start: date,
        end: date,
        now: datetime,
    ) -> tuple[DailySeries, datetime] | None:
        cursor = self.collection.find(
            {
                "source_key": source_key(provider, latitude, longitude),
                "date": {"$gte": start.isoformat(), "$lte": end.isoformat()},
                # TTL deletion is asynchronous, so freshness is always part of the query.
                "expires_at": {"$gt": now},
            },
            projection={"_id": False},
        ).sort("date", ASCENDING)
        with storage_errors():
            documents = await cursor.to_list()
        if len(documents) != (end - start).days + 1:
            return None
        first = documents[0]
        resolved = (
            None
            if first["resolved_latitude"] is None
            else (first["resolved_latitude"], first["resolved_longitude"])
        )
        days = tuple(
            DailyValue(
                date.fromisoformat(d["date"]), d["tmax_c"], d["quality"], bool(d["duplicate_dates"])
            )
            for d in documents
        )
        series = DailySeries(
            provider,
            (latitude, longitude),
            resolved,
            first["elevation_m"],
            min(d["retrieved_at"] for d in documents),
            days,
        )
        return series, min(d["expires_at"] for d in documents)
