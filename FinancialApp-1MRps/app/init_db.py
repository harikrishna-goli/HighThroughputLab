from decimal import Decimal
from hashlib import sha256

from sqlalchemy import func, select

from database import write_SessionLocal, write_engine
from models import Account, Base


def hash_pin(pin: str) -> str:
    return sha256(pin.encode("utf-8")).hexdigest()


async def init_database():
    async with write_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with write_SessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(Account))

        if result.scalar_one() > 0:
            print("Primary database already has data. Skipping...")
            return

        print("Populating primary database (USER-0001 to USER-10000)...")

        accounts = []
        for user_num in range(1, 10001):
            user_id = f"USER-{user_num:04d}"
            pin = f"{user_num % 1000000:06d}"

            accounts.append(
                Account(
                    user_unique_id=user_id,
                    pin_hash=hash_pin(pin),
                    balance=Decimal(str(1000 + (user_num % 100000))),
                )
            )

            if len(accounts) % 1000 == 0:
                session.add_all(accounts)
                await session.commit()
                print(f"  Inserted {user_num:,} accounts...")
                accounts = []

        if accounts:
            session.add_all(accounts)
            await session.commit()

        total_result = await session.execute(select(func.count()).select_from(Account))
        total = total_result.scalar_one()
        print(f"Primary database: {total:,} accounts loaded\n")


if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("INITIALIZING DATABASE WITH DUMMY DATA")
    print("=" * 60 + "\n")
    asyncio.run(init_database())
    print("=" * 60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60 + "\n")
