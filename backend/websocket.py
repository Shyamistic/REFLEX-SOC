from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

clients = set()

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo/Ping (optional): await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        clients.remove(websocket)

# Utility: broadcast to all clients
async def broadcast_event(message: str):
    for ws in clients.copy():
        try:
            await ws.send_text(message)
        except:
            clients.discard(ws)
