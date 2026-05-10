from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BalanceRequest(BaseModel):
    user_unique_id: str = Field(min_length=5, max_length=64)
    PINCode: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class BalanceResponse(BaseModel):
    user_unique_id: str = Field(min_length=5, max_length=64)
    balance: Decimal = Field(ge=Decimal("0.00"), max_digits=14, decimal_places=2)

    model_config = ConfigDict(json_encoders={Decimal: lambda value: f"{value:.2f}"})

    @field_validator("balance")
    @classmethod
    def ensure_two_decimal_places(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))
