import json
import time
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://api.opendota.com/api"
TTL_SECONDS = 60 * 60 * 24  # 24 hours

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_MEMORY_CACHE: dict[str, tuple[float, Any]] = {}


def _cache_path(key: str) -> Path:
    safe_key = key.replace(":", "_")
    return CACHE_DIR / f"{safe_key}.json"


def _get_cached(key: str):
    # memory cache
    mem_entry = _MEMORY_CACHE.get(key)
    if mem_entry:
        ts, value = mem_entry
        if time.time() - ts <= TTL_SECONDS:
            return value

    # disk cache
    path = _cache_path(key)
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        ts = payload["ts"]
        value = payload["value"]

        if time.time() - ts > TTL_SECONDS:
            return None

        _MEMORY_CACHE[key] = (ts, value)
        return value
    except Exception:
        return None


def _set_cached(key: str, value: Any):
    ts = time.time()
    _MEMORY_CACHE[key] = (ts, value)

    path = _cache_path(key)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump({"ts": ts, "value": value}, f)
    except Exception:
        pass


def get_hero_matchups(hero_id: int) -> list[dict]:
    cache_key = f"matchups:{hero_id}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    url = f"{BASE_URL}/heroes/{hero_id}/matchups"
    response = requests.get(url, timeout=6)
    response.raise_for_status()

    data = response.json()
    _set_cached(cache_key, data)
    return data