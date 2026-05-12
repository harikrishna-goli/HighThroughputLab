import os
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_USER = os.getenv("DB_USER", "sharduser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "shardpass123")
DB_NAME = os.getenv("DB_NAME", "financial_db")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "50"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "100"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "10"))

WRITE_DB_HOST = os.getenv("WRITE_DB_HOST", "postgres-primary")
WRITE_DB_PORT = int(os.getenv("WRITE_DB_PORT", "5432"))
READ_DB_HOST = os.getenv("READ_DB_HOST", "haproxy-read")
READ_DB_PORT = int(os.getenv("READ_DB_PORT", "15432"))


def _dsn(host: str, port: int) -> str:
    user = quote_plus(DB_USER)
    pw = quote_plus(DB_PASSWORD)
    db = quote_plus(DB_NAME)
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"


def _create_engine(host: str, port: int):
    return create_async_engine(
        _dsn(host, port),
        pool_pre_ping=True,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=3600,
    )


write_engine = _create_engine(WRITE_DB_HOST, WRITE_DB_PORT)
read_engine = _create_engine(READ_DB_HOST, READ_DB_PORT)

write_SessionLocal = async_sessionmaker(bind=write_engine, expire_on_commit=False)
SessionLocal = async_sessionmaker(bind=read_engine, expire_on_commit=False)


def get_session(_: str | None = None) -> AsyncSession:
    """Get a read session via HAProxy, which balances across read replicas."""
    return SessionLocal()
