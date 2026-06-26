from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.services.auth import req_admin
from backend.database import get_db
from backend.models.users import User
from backend.schemas.drops import DropResponse, DropCreate
from backend.services.drop_service import dropGet,dropCreate

router = APIRouter()

@router.get("/admin/drops", response_model=list[DropResponse])
def get_drop(
    admin: User = Depends(req_admin),
    db: Session = Depends(get_db)
    ):

    return dropGet(db)


@router.post("/admin/drops")
def create_drop(
    drop: DropCreate,
    admin:User = Depends(req_admin), 
    db: Session=Depends(get_db)
):
    return dropCreate(drop, db)