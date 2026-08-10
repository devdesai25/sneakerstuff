from pydantic import BaseModel, ConfigDict
from typing import Optional

class EntryRequest(BaseModel):
    address: str
    size: str = "US 9"
    captcha_token: Optional[str] = None
    device_fingerprint: Optional[str] = None

class ReservationResponse(BaseModel):
    reservation_id: int
    order_id: int
    order_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EntryResponse(BaseModel):
    entry_id: int
    drop_id: int
    user_id: int
    ranking: Optional[int] = None
    address: str
    size: str
    device_fingerprint: Optional[str] = None
    reservation: Optional[ReservationResponse] = None

    model_config = ConfigDict(from_attributes=True)