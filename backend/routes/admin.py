from fastapi import APIRouter, Depends, HTTPException
from services.auth import req_admin
from models.users import User

router = APIRouter( 
    tags=["admin"]
)

@router.post("/admin")
def admin(
    current_user : User = Depends(req_admin)
):
    
    return current_user