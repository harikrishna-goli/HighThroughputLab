from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_unique_id = Column(String(64), unique=True, nullable=False, index=True)
    pin_hash = Column(String(64), nullable=False)
    balance = Column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
