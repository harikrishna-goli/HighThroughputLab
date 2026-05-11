import json
import os
from dataclasses import dataclass
from decimal import Decimal

from redis.asyncio import Redis
from redis.exceptions import RedisError


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
ACCOUNT_CACHE_TTL_SECONDS = int(os.getenv("ACCOUNT_CACHE_TTL_SECONDS", "30"))


redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


@dataclass(frozen=True)
class CachedAccount:
    user_unique_id: str
    pin_hash: str
    balance: Decimal


def account_cache_key(user_unique_id: str) -> str:
    return f"account:{user_unique_id}"


async def get_cached_account(user_unique_id: str) -> CachedAccount | None:
    try:
        cached_value = await redis_client.get(account_cache_key(user_unique_id))
    except RedisError:
        return None

    if cached_value is None:
        return None

    try:
        data = json.loads(cached_value)
        return CachedAccount(
            user_unique_id=user_unique_id,
            pin_hash=data["pin_hash"],
            balance=Decimal(data["balance"]),
        )
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return None


async def set_cached_account(account: CachedAccount) -> None:
    cache_value = json.dumps(
        {
            "pin_hash": account.pin_hash,
            "balance": f"{account.balance:.2f}",
        }
    )

    try:
        await redis_client.set(
            account_cache_key(account.user_unique_id),
            cache_value,
            ex=ACCOUNT_CACHE_TTL_SECONDS,
        )
    except RedisError:
        return


async def close_cache() -> None:
    await redis_client.aclose()
