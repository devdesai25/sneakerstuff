from pydantic import BaseModel
from backend.models.users import User

class UserLogin(BaseModel):
    username :str
    password :str
    

class UserSignup(BaseModel):
    username :str
    password :str


class UserResponse(BaseModel):

    id: int
    role: str
    username: str

    class config:
        orm_mode = True