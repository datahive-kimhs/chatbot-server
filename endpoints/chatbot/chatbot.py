import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger
from starlette.types import Message

from core.chatbot import make_answer
from schema.response import ChatResponse
from schema.chatbot import ChatData

chatbot_router = APIRouter(prefix='/chatbot')

async def send_json_unicode(websocket: WebSocket, message: Message) -> None:
    """
    This function for unicode language.
    :param websocket: websocket instance.
    :param message: dict
    """
    text = json.dumps(message, ensure_ascii=False)
    await websocket.send({"type": "websocket.send", "text": text})


@chatbot_router.post("/", response_model=ChatResponse)
async def chatbot_http_endpoint(chat_data: ChatData):
    answer = make_answer(chat_data)
    return answer


@chatbot_router.websocket("/")
async def chatbot_websocket_endpoint(
        websocket: WebSocket
):
    
    await websocket.accept()
    # Preprocess chat room - load chat log, etc...
    
    try:
        while True:
            # data = await websocket.receive_text()
            data_json = await websocket.receive_json()
            # data = data_json.get('Query', 'Lang')
            data = data_json.get("q")

            # make answer...
            send_data = make_answer(data_json)

            # send_data = make_answer(data)
            send_data = {"a_kr": "ㅎㅇㅎㅇ",
                         "a_en": "hello"}
            logger.info(f"receive data = {data}")
            # await websocket.send_text(send_data)
            await send_json_unicode(websocket, send_data)
            logger.info(f"send data = {send_data}")
    except WebSocketDisconnect as e:
        # exit chatbot
        logger.exception(e)
        return "ByeBye"
