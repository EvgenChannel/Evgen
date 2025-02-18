from fastapi import WebSocket
from database import get_user_by_username, create_user

# Аутентификация пользователя по имени
async def authenticate(websocket: WebSocket):
    await websocket.accept()
    username = await websocket.receive_text()  # Получаем имя пользователя от клиента

    user = get_user_by_username(username)
    if not user:
        user_id = create_user(username)  # Если пользователя нет, создаем нового
    else:
        user_id = user[0]

    return user_id
