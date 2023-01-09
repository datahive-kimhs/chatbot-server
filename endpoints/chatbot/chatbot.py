from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger

from core.chatbot import make_answer

chatbot_router = APIRouter(prefix='/chatbot')


@chatbot_router.websocket("/{room_id}")
@chatbot_router.websocket("/test")
async def chatbot_endpoint(
        websocket: WebSocket,
        room_id: str
):
    await websocket.accept()
    # Preprocess chat room - load chat log, etc...
    try:
        while True:
            data = await websocket.receive_text()
            # data_json = await websocket.receive_json()

            # make answer...
            send_data = make_answer(data)

            logger.info(f"{room_id}\treceive data = {data}")
            await websocket.send_text(send_data)
            logger.info(f"{room_id}\tsend data = {send_data}")
    except WebSocketDisconnect as e:
        # exit chatbot
        logger.exception(e)
        pass
