"""MongoDB repositories; the only modules that query collections."""

from collections.abc import Iterator
from contextlib import contextmanager

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import CollectionInvalid, PyMongoError

from app.database import DatabaseUnavailable, safe_reason


@contextmanager
def storage_errors() -> Iterator[None]:
    try:
        yield
    except PyMongoError as exc:
        raise DatabaseUnavailable(safe_reason(exc)) from None


async def ensure_collection(database: AsyncDatabase, name: str, validator: dict) -> None:
    try:
        await database.create_collection(name, validator=validator)
    except CollectionInvalid:
        pass
