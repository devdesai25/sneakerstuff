from pydantic import BaseModel

class EntryRequest(BaseModel):
    address: str

class EntryResponse(BaseModel):
    entry_id: int
    drop_id: int
    user_id: int
    ranking: int
    address: str