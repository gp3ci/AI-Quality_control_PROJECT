"""
Redis-backed Job Store
-----------------------
Drop-in replacement for the in-memory _JOB_STORE dict.

Why Redis?
  - Jobs survive API restarts / crashes (persistence)
  - Multiple API replicas share a single consistent view
  - Built-in TTL expiry — no manual cleanup loop needed
  - Celery workers can write job state and API processes read it

Usage (async):
    store = RedisJobStore(redis_client)
    await store.set(job_id, job_dict)
    job = await store.get(job_id)          # None if not found
    await store.delete(job_id)

The store JSON-serialises all values and handles JobStatus enum
serialisation/deserialisation transparently.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.models.schemas import JobStatus

logger = logging.getLogger(__name__)

# Default TTL: 24 hours (can be overridden per-entry)
DEFAULT_TTL_SECONDS = 86_400


class RedisJobStore:
    """
    Async Redis-backed job store.
    All values are JSON-serialised; JobStatus enums are stored as strings
    and re-hydrated on read.
    """

    def __init__(self, client: aioredis.Redis, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        self._r = client
        self._ttl = ttl

    def _key(self, job_id: str) -> str:
        return f"telecom_job:{job_id}"

    def _serialise(self, data: dict) -> str:
        """Convert dict to JSON, turning enums into strings."""
        def default(obj):
            if isinstance(obj, JobStatus):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")
        return json.dumps(data, default=default)

    def _deserialise(self, raw: str | bytes) -> dict:
        """Parse JSON and re-hydrate JobStatus enum."""
        data = json.loads(raw)
        if "status" in data and isinstance(data["status"], str):
            try:
                data["status"] = JobStatus(data["status"])
            except ValueError:
                pass
        return data

    async def set(self, job_id: str, data: dict, ttl: int | None = None) -> None:
        """Persist a job record to Redis."""
        await self._r.set(
            self._key(job_id),
            self._serialise(data),
            ex=ttl or self._ttl,
        )

    async def get(self, job_id: str) -> dict | None:
        """Retrieve a job record, or None if not found / expired."""
        raw = await self._r.get(self._key(job_id))
        if raw is None:
            return None
        return self._deserialise(raw)

    async def update(self, job_id: str, updates: dict) -> dict | None:
        """
        Merge updates into an existing job record (read-modify-write).
        Returns the updated record, or None if the job doesn't exist.
        """
        existing = await self.get(job_id)
        if existing is None:
            logger.warning(f"[store] update called on non-existent job {job_id!r}")
            return None
        existing.update(updates)
        await self.set(job_id, existing)
        return existing

    async def delete(self, job_id: str) -> None:
        """Delete a job record from Redis."""
        await self._r.delete(self._key(job_id))

    async def exists(self, job_id: str) -> bool:
        """Returns True if the job record exists in Redis."""
        return bool(await self._r.exists(self._key(job_id)))


# ─────────────────────────────────────────────────────────────────────────────
#  Fallback: In-memory dict store (used when Redis is unavailable)
# ─────────────────────────────────────────────────────────────────────────────

class InMemoryJobStore:
    """
    Thread-safe in-memory fallback store (used when Redis is not configured).
    Equivalent API to RedisJobStore but backed by a plain dict.
    Warning: State is lost on process restart.
    """

    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    async def set(self, job_id: str, data: dict, ttl: int | None = None) -> None:
        self._data[job_id] = data

    async def get(self, job_id: str) -> dict | None:
        return self._data.get(job_id)

    async def update(self, job_id: str, updates: dict) -> dict | None:
        existing = self._data.get(job_id)
        if existing is None:
            return None
        existing.update(updates)
        return existing

    async def delete(self, job_id: str) -> None:
        self._data.pop(job_id, None)

    async def exists(self, job_id: str) -> bool:
        return job_id in self._data
