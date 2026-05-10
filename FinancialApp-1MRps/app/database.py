import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_USER = os.getenv("DB_USER", "sharduser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "shardpass123")
DB_NAME = os.getenv("DB_NAME", "financial_db")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "50"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "100"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "10"))

SHARD_HOSTS = ["postgres-shard-1", "postgres-shard-2", "postgres-shard-3", "postgres-shard-4"]
SHARD_PORTS = [5432, 5432, 5432, 5432]

engines = [
    create_async_engine(
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{SHARD_HOSTS[i]}:{SHARD_PORTS[i]}/{DB_NAME}",
        pool_pre_ping=True,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=3600,
    )
    for i in range(4)
]

SessionLocals = [
    async_sessionmaker(bind=engine, expire_on_commit=False)
    for engine in engines
]


def get_shard_id(user_unique_id: str) -> int:
    """
    Determine shard based on user number.
    Shard 0: USER-0001 to USER-2500
    Shard 1: USER-2501 to USER-5000
    Shard 2: USER-5001 to USER-7500
    Shard 3: USER-7501 to USER-10000
    """
    user_num = int(user_unique_id.split("-")[1])
    if user_num <= 2500:
        return 0
    elif user_num <= 5000:
        return 1
    elif user_num <= 7500:
        return 2
    else:
        return 3


def get_session(user_unique_id: str) -> AsyncSession:
    """Get database session for user's shard."""
    shard_id = get_shard_id(user_unique_id)
    return SessionLocals[shard_id]()
