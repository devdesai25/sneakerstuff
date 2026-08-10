from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth import req_admin
from backend.database import get_db
from backend.enums.drop_status import DropStatus
from backend.models.users import User
from backend.models.drops import Drop
from backend.schemas.drops import DropResponse, DropCreate, DropUpdate
from backend.services.drop_service import (
    drop_get, drop_create, 
    drop_delete, drop_update, 
    drop_cancel, drop_publish,
    drop_pause, drop_resume, drop_draw, execute_drop_draw
)
from backend.services.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/drops/{drop_id}")
async def websocket_drop_endpoint(websocket: WebSocket, drop_id: int):
    """WebSocket endpoint for real-time drop status and entry updates."""
    await manager.connect(websocket, drop_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, drop_id)
    except Exception:
        manager.disconnect(websocket, drop_id)

@router.get("/drops/{drop_id}/stream")
async def sse_drop_stream(drop_id: int):
    """SSE endpoint for serverless environments (Vercel compatibility)."""
    async def event_generator():
        yield f"data: {json.dumps({'event': 'connected', 'drop_id': drop_id})}\n\n"
        while True:
            await asyncio.sleep(15)
            yield f"data: {json.dumps({'event': 'heartbeat'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/drops", response_model = list[DropResponse])
async def get_public_drops(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all published drops (excluding DRAFT and hidden statuses) for public users."""
    from datetime import datetime, timezone

    stmt = select(Drop).where(Drop.status != DropStatus.DRAFT, Drop.is_visible == True)
    result = await db.execute(stmt)
    drops = result.scalars().all()

    now = datetime.now(timezone.utc)
    updated = False
    for drop in drops:
        if drop.status in (DropStatus.SCHEDULED, DropStatus.ENTRY_OPEN) and now >= drop.closes_at:
            drop.status = DropStatus.ENTRY_CLOSED
            updated = True

    if updated:
        await db.commit()

    return drops

@router.get("/admin/drop", response_model = list[DropResponse])
async def get_drop(
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):

    return await drop_get(db)

@router.post("/admin/drop", response_model = DropResponse)
async def create_drop(
    drop: DropCreate,
    admin: User = Depends(req_admin), 
    db: AsyncSession = Depends(get_db)
):
    return await drop_create(drop, db)

@router.patch("/admin/drop/{id}", response_model = DropResponse)
async def update_drop(
    id: int,
    drop: DropUpdate,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_update(id, drop, db)

@router.delete("/admin/drop/{id}/delete")
async def delete_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_delete(id, db)

@router.patch("/admin/drop/{id}/cancel", response_model=DropResponse)
async def cancel_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    
    return await drop_cancel(id, db)

@router.patch("/admin/drop/{id}/publish", response_model=DropResponse)
async def publish_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    return await drop_publish(id, db)

@router.patch("/admin/drop/{id}/toggle-visibility", response_model=DropResponse)
async def toggle_drop_visibility(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    """Toggle drop visibility status for public users."""
    from backend.helpers.drop_helpers import get_drop_or_404
    drop = await get_drop_or_404(id, db)
    drop.is_visible = not drop.is_visible
    await db.commit()
    await db.refresh(drop)
    return drop

@router.patch("/admin/drop/{id}/pause", response_model=DropResponse)
async def pause_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    return await drop_pause(id, db)

@router.patch("/admin/drop/{id}/resume", response_model=DropResponse)
async def resume_drop(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    return await drop_resume(id, db)

@router.post("/admin/drop/{id}/draw", response_model=DropResponse)
async def trigger_drop_draw(
    id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession = Depends(get_db)
):
    return await drop_draw(id, db)
