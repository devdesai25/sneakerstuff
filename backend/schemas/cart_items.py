from pydantic import BaseModel, ConfigDict

class CartResponse(BaseModel):
    
    product_id: int
    name: str
    price: float
    image: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class CartCreate(BaseModel):
    
    product_id: int
    quantity: int

class CartPatch(BaseModel):
    
    quantity: int