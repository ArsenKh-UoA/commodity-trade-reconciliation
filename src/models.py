from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Literal

class CommodityTrade(BaseModel):
    Trade_ID: str
    Date: date
    Commodity_Index: Literal["TTF", "NBP", "Henry Hub"]
    Counterparty: str
    Direction: Literal["BUY", "SELL"]
    Volume_MMBtu: int = Field(gt=0, description="Volume must be strictly positive")
    Price_USD: float = Field(gt=0.0, description="Price must be strictly positive")

    # Custom validator to handle string clean up if needed
    @field_validator('Counterparty', mode='before')
    def check_empty_string(cls, v):
        if not v or str(v).strip() == "" or str(v).lower() == "none":
            raise ValueError("Counterparty cannot be empty")
        return str(v).strip()