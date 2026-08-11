import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps drop_id (int) -> Set of active WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Global connection set for all-drop overview
        self.global_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, drop_id: int = 0):
        await websocket.accept()
        if drop_id == 0:
            self.global_connections.add(websocket)
        else:
            if drop_id not in self.active_connections:
                self.active_connections[drop_id] = set()
            self.active_connections[drop_id].add(websocket)
        logger.info(f"WebSocket connected for drop_id={drop_id}")

    def disconnect(self, websocket: WebSocket, drop_id: int = 0):
        if drop_id == 0:
            self.global_connections.discard(websocket)
        elif drop_id in self.active_connections:
            self.active_connections[drop_id].discard(websocket)
            if not self.active_connections[drop_id]:
                del self.active_connections[drop_id]
        logger.info(f"WebSocket disconnected for drop_id={drop_id}")

    async def broadcast_to_drop(self, drop_id: int, message: dict):
        payload = json.dumps(message)
        
        # 1. Send to subscribers of specific drop
        if drop_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[drop_id]:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.warning(f"Failed to send WS message to drop {drop_id}: {e}")
                    disconnected.add(connection)
            for conn in disconnected:
                self.disconnect(conn, drop_id)

        # 2. Send to subscribers of global overview
        disconnected_global = set()
        for connection in self.global_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send WS message to global listener: {e}")
                disconnected_global.add(connection)
        for conn in disconnected_global:
            self.disconnect(conn, 0)

manager = ConnectionManager()
