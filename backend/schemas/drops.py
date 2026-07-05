from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductSummary(BaseModel):
    product_id : int
    name : str
    images : str | None = None

    model_config = ConfigDict(from_attributes=True)

class DropResponse(BaseModel):
    drop_id : int
    status : str   
    opens_at : datetime
    closes_at : datetime
    drop_inventory : int
    product_price : Decimal | None = None
    product_name : str | None = None
    product_image : str | None = None

    model_config = ConfigDict(from_attributes=True)

class DropCreate(BaseModel):
    product_id : int
    opens_at : datetime
    closes_at : datetime
    drop_inventory : int

class DropUpdate(BaseModel):
    opens_at : Optional[datetime] = None
    closes_at : Optional[datetime] = None
    drop_inventory : Optional[int] = None
    product_price : Optional[float] = None
    product_name : Optional[float] = None
    product_image : Optional[str] = None