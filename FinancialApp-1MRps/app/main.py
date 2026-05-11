from hashlib import sha256
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select

from schemas import BalanceRequest, BalanceResponse
from models import Account
from database import get_session
from cache import CachedAccount, close_cache, get_cached_account, set_cached_account


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_cache()


app = FastAPI(title="Financial Read API", lifespan=lifespan)


def hash_pin(pin_code: str) -> str:
    return sha256(pin_code.encode("utf-8")).hexdigest()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/read/balance", response_model=BalanceResponse)
async def read_balance(request: BalanceRequest) -> BalanceResponse:
    requested_pin_hash = hash_pin(request.PINCode)
    cached_account = await get_cached_account(request.user_unique_id)
    if cached_account is not None:
        if cached_account.pin_hash != requested_pin_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user_unique_id or PINCode",
            )

        return BalanceResponse(
            user_unique_id=cached_account.user_unique_id,
            balance=cached_account.balance,
        )

    async with get_session(request.user_unique_id) as session:
        result = await session.execute(
            select(Account.user_unique_id, Account.pin_hash, Account.balance).where(
                Account.user_unique_id == request.user_unique_id
            )
        )
        account = result.one_or_none()

        if account is None or account.pin_hash != requested_pin_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user_unique_id or PINCode",
            )

        await set_cached_account(
            CachedAccount(
                user_unique_id=account.user_unique_id,
                pin_hash=account.pin_hash,
                balance=account.balance,
            )
        )

        return BalanceResponse(
            user_unique_id=account.user_unique_id,
            balance=account.balance,
        )
