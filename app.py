import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from data.load_data import load_dataset
from data.load_data import dataset_bm25
from data.load_model import load_model

from endpoints.chatbot.chatbot import chatbot_router
from endpoints.chatbot.chatroom import chatroom_router
from config import server_config

debug = server_config.getboolean('DEFAULT', 'Debug')
app = FastAPI(debug=debug)

# set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add route
app.include_router(chatbot_router)
app.include_router(chatroom_router)


@app.route("/")
async def main():
    return {"status": "ok"}


if __name__ == "__main__":
    if debug:
        # for debug
        import uvicorn
        uvicorn.run(app,
                    host=server_config.get('SERVER', 'Host'),
                    port=server_config.getint('SERVER', 'Port'),
                    log_level=logging.DEBUG)
