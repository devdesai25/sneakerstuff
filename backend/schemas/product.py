from pydantic import BaseModel
from typing import Optional

class ProductResponse(BaseModel):
    product_id : int
    name : str
    description: str
    price : float
    images: str | None = None
    class config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    stock : Optional[int] = None
    price : Optional[float] = None
    images: str | None = None
    
class ProductCreate(BaseModel):

    name : str
    description : str | None = None
    stock : int
    price : float 
    images: str | None = None