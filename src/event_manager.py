from typing import Set

from fastapi import WebSocket


class EventManager:
    """
    Observable/Event manager.
    """

    def __init__(self):
        self.connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)

    async def notify(self, event: dict):
        disconnected = set()

        for websocket in self.connections:
            try:
                await websocket.send_json(event)
            except Exception:
                disconnected.add(websocket)

        for websocket in disconnected:
            self.connections.discard(websocket)


event_manager = EventManager()