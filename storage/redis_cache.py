"""Caching layer using Redis."""
import hashlib
import json
from typing import Any, Optional

from config import REDIS_URL
from utils.logger import get_logger

logger = get_logger(__name__)

_redis_client = None


def get_cache():
    """Lazy Redis connection. Returns None if Redis unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL)
        _redis_client.ping()
        return _redis_client
    except Exception as e:
        logger.warning("Redis not available: %s", e)
        _redis_client = None
        return None


def _key(prefix: str, raw: str) -> str:
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{h}"


def cache_get(key_prefix: str, raw_input: str) -> Optional[Any]:
    """Get cached value for this input. Returns None if miss or Redis down."""
    r = get_cache()
    if r is None:
        return None
    try:
        k = _key(key_prefix, raw_input)
        val = r.get(k)
        if val is None:
            return None
        return json.loads(val)
    except Exception as e:
        logger.debug("Cache get error: %s", e)
        return None


def cache_set(key_prefix: str, raw_input: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Set cache for this input."""
    r = get_cache()
    if r is None:
        return
    try:
        k = _key(key_prefix, raw_input)
        r.setex(k, ttl_seconds, json.dumps(value))
    except Exception as e:
        logger.debug("Cache set error: %s", e)
