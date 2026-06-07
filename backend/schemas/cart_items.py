from pydantic import BaseModel

class CartResponse(BaseModel):
    
    product_id: int
    name: str
    price: float
    image: str
    quantity: int

    class Config:
        from_attributes = True

class CartCreate(BaseModel):
    
    product_id: int
    quantity: int

class CartPatch(BaseModel):
    
    quantity: int