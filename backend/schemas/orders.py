from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OrderItemsSummary(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    order_id: int
    total_amount: float
    status: str
    expires_at: datetime
    address: str

    order_items: list[OrderItemsSummary] 

    model_config = ConfigDict(from_attributes=True)

class OrderRequest(BaseModel):
    address: str
