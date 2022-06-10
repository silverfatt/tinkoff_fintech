from typing import Any

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from redis import Redis  # type: ignore

from app.connections import ConnectionManager
from app.html import html
from app.redis import add_message_to_redis
from app.setup import (
    CLIENT_ID_LOWER_BORDER,
    CLIENT_ID_UPPER_BORDER,
    MESSAGE_TEXT_LOWER_BORDER,
)


def get_redis() -> Redis:  # pragma: no cover
    return Redis(host='redis', port=6379, decode_responses=False)


app = FastAPI()
manager = ConnectionManager()


@app.get('/')
async def get() -> HTMLResponse:
    return HTMLResponse(html)


def format_last_messages(redis_client: Redis) -> str:
    messages = ''
    if not redis_client.get('messages'):
        redis_client.set('messages', '0')
    for i in range(1, int(redis_client.get('messages')) + 1):
        message = str(redis_client.get(str(i))) + '\n'
        client_id = message[CLIENT_ID_LOWER_BORDER:CLIENT_ID_UPPER_BORDER]
        text = message[MESSAGE_TEXT_LOWER_BORDER : len(message) - 1]
        messages += f'|  From {client_id}: {text}  |'
    return messages


@app.get('/last_messages')
async def get_last_messages(redis_client: Redis = Depends(get_redis)) -> Any:
    return format_last_messages(redis_client)


@app.websocket('/ws/{client_id}')
async def websocket_endpoint(
    websocket: WebSocket, client_id: int, redis_client: Redis = Depends(get_redis)
) -> Any:  # pragma: no cover
    if not redis_client.get('messages'):
        redis_client.set('messages', '0')
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            add_message_to_redis(redis_client, client_id, data)
            await manager.send_personal_message(f'Sent: {data}', websocket)
            await manager.broadcast(f'User{client_id} says: {data}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f'User{client_id} left the chat')
