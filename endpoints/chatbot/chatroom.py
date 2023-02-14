import uuid

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.logger import logger

# from core.chatroom import

chatroom_router = APIRouter(prefix='/chatroom')


@chatroom_router.put('/')
async def create_chatbot_room(request: Request):
    chatroom_id = request.cookies.get('chatroom_id')
    if chatroom_id is None:
        chatroom_id = uuid.uuid4()
    return RedirectResponse()


@chatroom_router.post('/{room_id}')
async def update_chatbot_room():
    pass


@chatroom_router.get('/{room_id}')
async def chatbot_room_info():
    pass
