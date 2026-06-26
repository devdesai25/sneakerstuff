from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

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

    product : ProductSummary

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
