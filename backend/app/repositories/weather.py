"""Normalized daily maxima, one document per source key and calendar year (docs/database.md)."""

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta

from pymongo import ASCENDING, ReplaceOne
from pymongo.asynchronous.database import AsyncDatabase

from app.ingestion import NORMALIZATION_VERSION, DailySeries, DailyValue
from app.repositories import ensure_collection, storage_errors
from app.schemas import SOURCE_PROFILES, ProviderName

COLLECTION = "weather_years"
VALID_TTL = timedelta(days=30)
NEGATIVE_TTL = timedelta(hours=1)
QUALITY_CODES = {"valid": "v", "missing": "m", "invalid": "i"}
QUALITY_NAMES = {code: name for name, code in QUALITY_CODES.items()}
NUMBER_OR_NULL = {"bsonType": ["double", "null"]}
VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "source_key",
            "provider",
            "year",
            "tmax_c",
            "quality",
            "duplicate_days",
            "normalization_version",
            "retrieved_at",
            "expires_at",
        ],
        "properties": {
            "source_key": {"bsonType": "string"},
            "provider": {"enum": list(SOURCE_PROFILES)},
            "year": {"bsonType": "int", "minimum": 1940, "maximum": 2200},
            "tmax_c": {
                "bsonType": "array",
                "minItems": 365,
                "maxItems": 366,
                "items": NUMBER_OR_NULL,
            },
            "quality": {"bsonType": "string", "pattern": "^[vmi]{365,366}$"},
            "duplicate_days": {
                "bsonType": "array",
                "items": {"bsonType": "int", "minimum": 0, "maximum": 365},
            },
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


def _require_whole_years(start: date, end: date) -> None:
    if start > end or (start.month, start.day, end.month, end.day) != (1, 1, 12, 31):
        raise ValueError("Weather storage holds whole calendar years only")


def _days_in(year: int) -> int:
    return 366 if calendar.isleap(year) else 365


class WeatherRepository:
    def __init__(self, database: AsyncDatabase):
        self.database = database
        self.collection = database[COLLECTION]

    async def ensure_schema(self) -> None:
        await ensure_collection(self.database, COLLECTION, VALIDATOR)
        await self.collection.create_index(
            [("source_key", ASCENDING), ("year", ASCENDING)], unique=True, name="source_year"
        )
        await self.collection.create_index("expires_at", expireAfterSeconds=0, name="expiry")

    async def save(self, series: DailySeries) -> None:
        _require_whole_years(series.days[0].day, series.days[-1].day)
        key = source_key(series.provider, *series.requested)
        resolved = series.resolved or (None, None)
        years: dict[int, list[DailyValue]] = defaultdict(list)
        for day in series.days:
            years[day.day.year].append(day)
        operations = []
        for year, days in years.items():
            if len(days) != _days_in(year):
                raise ValueError("Weather storage holds whole calendar years only")
            all_valid = all(day.quality == "valid" for day in days)
            document = {
                "source_key": key,
                "provider": series.provider,
                "year": year,
                "requested_latitude": float(series.requested[0]),
                "requested_longitude": float(series.requested[1]),
                "resolved_latitude": resolved[0],
                "resolved_longitude": resolved[1],
                "elevation_m": series.elevation_m,
                "tmax_c": [day.tmax_c for day in days],
                "quality": "".join(QUALITY_CODES[day.quality] for day in days),
                "duplicate_days": [index for index, day in enumerate(days) if day.duplicate],
                "normalization_version": NORMALIZATION_VERSION,
                "retrieved_at": series.retrieved_at,
                # A year with any gap expires like a negative-cache entry, so it is refetched soon.
                "expires_at": series.retrieved_at + (VALID_TTL if all_valid else NEGATIVE_TTL),
            }
            operations.append(ReplaceOne({"source_key": key, "year": year}, document, upsert=True))
        with storage_errors():
            await self.collection.bulk_write(operations, ordered=False)

    async def load(
        self,
        provider: ProviderName,
        latitude: float,
        longitude: float,
        start: date,
        end: date,
        now: datetime,
    ) -> tuple[DailySeries, datetime] | None:
        _require_whole_years(start, end)
        cursor = self.collection.find(
            {
                "source_key": source_key(provider, latitude, longitude),
                "year": {"$gte": start.year, "$lte": end.year},
                # TTL deletion is asynchronous, so freshness is always part of the query.
                "expires_at": {"$gt": now},
            },
            projection={"_id": False},
        ).sort("year", ASCENDING)
        with storage_errors():
            documents = await cursor.to_list()
        if [d["year"] for d in documents] != list(range(start.year, end.year + 1)):
            return None
        days: list[DailyValue] = []
        for document in documents:
            first_day = date(document["year"], 1, 1)
            duplicates = set(document["duplicate_days"])
            values, codes = document["tmax_c"], document["quality"]
            if not len(values) == len(codes) == _days_in(document["year"]):
                return None
            days.extend(
                DailyValue(
                    first_day + timedelta(days=i), value, QUALITY_NAMES[code], i in duplicates
                )
                for i, (value, code) in enumerate(zip(values, codes, strict=True))
            )
        first = documents[0]
        resolved = (
            None
            if first["resolved_latitude"] is None
            else (first["resolved_latitude"], first["resolved_longitude"])
        )
        series = DailySeries(
            provider,
            (latitude, longitude),
            resolved,
            first["elevation_m"],
            min(d["retrieved_at"] for d in documents),
            tuple(days),
        )
        return series, min(d["expires_at"] for d in documents)
