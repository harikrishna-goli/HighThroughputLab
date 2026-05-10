from hashlib import sha256
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select

from init_db import init_all_shards
from schemas import BalanceRequest, BalanceResponse
from models import Account
from database import get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_all_shards()
    yield


app = FastAPI(title="Financial Read API", lifespan=lifespan)


def hash_pin(pin_code: str) -> str:
    return sha256(pin_code.encode("utf-8")).hexdigest()


@app.post("/read/balance", response_model=BalanceResponse)
async def read_balance(request: BalanceRequest) -> BalanceResponse:
    async with get_session(request.user_unique_id) as session:
        result = await session.execute(
            select(Account.user_unique_id, Account.pin_hash, Account.balance).where(
                Account.user_unique_id == request.user_unique_id
            )
        )
        account = result.one_or_none()

        if account is None or account.pin_hash != hash_pin(request.PINCode):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user_unique_id or PINCode",
            )

        return BalanceResponse(
            user_unique_id=account.user_unique_id,
            balance=account.balance,
        )
