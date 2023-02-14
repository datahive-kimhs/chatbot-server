import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger
from starlette.types import Message

from core.chatbot import make_answer


chatbot_router = APIRouter(prefix='/chatbot')


async def send_json_unicode(websocket: WebSocket, message: Message) -> None:
    """
    This function for unicode language.
    :param websocket: websocket instance.
    :param message: dict
    """
    text = json.dumps(message, ensure_ascii=False)
    await websocket.send({"type": "websocket.send", "text": text})


@chatbot_router.websocket("/{room_id}")
async def chatbot_endpoint(
        websocket: WebSocket,
        room_id: str
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
            logger.info(f"{room_id}\treceive data = {data}")
            # await websocket.send_text(send_data)
            await send_json_unicode(websocket, send_data)
            logger.info(f"{room_id}\tsend data = {send_data}")
    except WebSocketDisconnect as e:
        # exit chatbot
        logger.exception(e)
        return "ByeBye"
