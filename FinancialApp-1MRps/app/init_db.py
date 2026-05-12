from hashlib import sha256
from decimal import Decimal
from sqlalchemy import func, select
from models import Base, Account
from database import write_SessionLocals, write_engines

def hash_pin(pin: str) -> str:
    return sha256(pin.encode("utf-8")).hexdigest()

async def init_all_shards():
    ranges = [(1, 2500), (2501, 5000), (5001, 7500), (7501, 10000)]

    for shard_id, engine in enumerate(write_engines):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async with write_SessionLocals[shard_id]() as session:
            result = await session.execute(select(func.count()).select_from(Account))

            # Check if already populated
            if result.scalar_one() > 0:
                print(f"Shard {shard_id + 1} already has data. Skipping...")
                continue

            start, end = ranges[shard_id]
            print(f"Populating Shard {shard_id + 1} (USER-{start:04d} to USER-{end:04d})...")

            accounts = []
            for user_num in range(start, end + 1):
                user_id = f"USER-{user_num:04d}"
                pin = f"{user_num % 1000000:06d}"

                account = Account(
                    user_unique_id=user_id,
                    pin_hash=hash_pin(pin),
                    balance=Decimal(str(1000 + (user_num % 100000)))
                )
                accounts.append(account)

                if len(accounts) % 1000 == 0:
                    session.add_all(accounts)
                    await session.commit()
                    print(f"  Inserted {len(accounts):,} accounts...")
                    accounts = []

            if accounts:
                session.add_all(accounts)
                await session.commit()

            total_result = await session.execute(select(func.count()).select_from(Account))
            total = total_result.scalar_one()
            print(f"✓ Shard {shard_id + 1}: {total:,} accounts loaded\n")

if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("INITIALIZING DATABASE WITH DUMMY DATA")
    print("=" * 60 + "\n")
    asyncio.run(init_all_shards())
    print("=" * 60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60 + "\n")
