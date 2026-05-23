from fastapi import APIRouter, Depends, HTTPException
from services.auth import req_admin

router = APIRouter( 
    tags=["admin"]
)

@router.post("/admin")
def admin(
    current_user = Depends(req_admin)
):
    
    return current_user