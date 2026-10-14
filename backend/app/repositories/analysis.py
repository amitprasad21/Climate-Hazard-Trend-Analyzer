"""Cached analysis payloads keyed by canonical scientific inputs (collection analysis_cache)."""

from datetime import datetime

from pymongo.asynchronous.database import AsyncDatabase

from app.climate import METHOD_VERSION
from app.repositories import ensure_collection, storage_errors
from app.schemas import CONTRACT_VERSION

COLLECTION = "analysis_cache"
VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "cache_key",
            "result",
            "method_version",
            "contract_version",
            "created_at",
            "expires_at",
            "source_fingerprint",
        ],
        "properties": {
            "cache_key": {"bsonType": "string"},
            "result": {"bsonType": "object"},
            "method_version": {"bsonType": "string"},
            "contract_version": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "expires_at": {"bsonType": "date"},
            "source_fingerprint": {"bsonType": "string"},
        },
    }
}


class AnalysisCacheRepository:
    def __init__(self, database: AsyncDatabase):
        self.database = database
        self.collection = database[COLLECTION]

    async def ensure_schema(self) -> None:
        await ensure_collection(self.database, COLLECTION, VALIDATOR)
        await self.collection.create_index("cache_key", unique=True, name="cache_key")
        await self.collection.create_index("expires_at", expireAfterSeconds=0, name="expiry")

    async def get(self, cache_key: str, now: datetime) -> dict | None:
        with storage_errors():
            document = await self.collection.find_one(
                {
                    "cache_key": cache_key,
                    "expires_at": {"$gt": now},
                    "method_version": METHOD_VERSION,
                    "contract_version": CONTRACT_VERSION,
                },
                projection={"_id": False, "result": True},
            )
        return document["result"] if document else None

    async def put(
        self,
        cache_key: str,
        result: dict,
        created_at: datetime,
        expires_at: datetime,
        source_fingerprint: str,
    ) -> None:
        with storage_errors():
            await self.collection.replace_one(
                {"cache_key": cache_key},
                {
                    "cache_key": cache_key,
                    "result": result,
                    "method_version": METHOD_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "created_at": created_at,
                    "expires_at": expires_at,
                    "source_fingerprint": source_fingerprint,
                },
                upsert=True,
            )
