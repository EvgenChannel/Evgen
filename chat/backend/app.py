from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from database import save_message, get_messages_for_chat, create_chat, get_chat_by_name
from auth import authenticate
from typing import List
import json

app = FastAPI()

# Словарь для хранения активных WebSocket-соединений
active_users: List[WebSocket] = {}

# Главная страница
@app.get("/")
def get_html():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

# WebSocket-соединение для чата
@app.websocket("/ws/{chat_name}")
async def websocket_endpoint(websocket: WebSocket, chat_name: str):
    user_id = await authenticate(websocket)

    # Проверка существования чата
    chat = get_chat_by_name(chat_name)
    if not chat:
        chat_id = create_chat(chat_name)  # Если чат не существует, создаем новый
    else:
        chat_id = chat[0]

    active_users[user_id] = websocket

    # Отправляем историю сообщений при подключении
    messages = get_messages_for_chat(chat_id)
    for msg in messages:
        await websocket.send_text(f"{msg[2]}: {msg[0]}")

    try:
        while True:
            data = await websocket.receive_text()  # Получаем сообщение от клиента
            # Сохраняем сообщение в базе данных
            save_message(chat_id, user_id, data)

            # Отправляем сообщение всем подключенным пользователям
            for user_ws in active_users.values():
                await user_ws.send_text(f"{user_id}: {data}")

    except WebSocketDisconnect:
        del active_users[user_id]  # Удаляем пользователя из активных соединений
