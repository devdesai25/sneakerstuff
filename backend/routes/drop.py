from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth import req_admin
from backend.database import get_db
from backend.models.users import User
from backend.schemas.drops import DropResponse, DropCreate, DropUpdate
from backend.services.drop_service import drop_get, drop_create, drop_delete, drop_update, drop_cancel, drop_publish

router = APIRouter()

@router.get("/admin/drops", response_model = list[DropResponse])
async def get_drop(
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
    ):

    return await drop_get(db)


@router.post("/admin/drops", response_model = DropResponse)
async def create_drop(
    drop: DropCreate,
    admin: User = Depends(req_admin), 
    db: AsyncSession = Depends(get_db)
):
    return await drop_create(drop, db)

@router.patch("/admin/drops/{id}", response_model = DropResponse)
async def update_drop(
    id: int,
    drop: DropUpdate,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_update(id, drop, db)

@router.delete("/admin/drops/{id}/delete")
async def delete_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_delete(id, db)

@router.post("/admin/drop/{id}/cancel", response_model=DropResponse)
async def cancel_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_cancel(id, db)

@router.post("/admin/drop/{id}/publish", response_model=DropResponse)
async def publish_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    return await drop_publish(id, db)
