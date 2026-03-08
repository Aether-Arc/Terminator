from fastapi import WebSocket

connections = []

async def connect(ws: WebSocket):

    await ws.accept()

    connections.append(ws)

async def broadcast(event):

    for ws in connections:

        await ws.send_json(event)