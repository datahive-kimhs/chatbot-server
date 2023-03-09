import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from endpoints.chatbot.chatbot import chatbot_router
from endpoints.chatbot.chatroom import chatroom_router
from config import server_config
from connection import connect_db as connect_db_to_ckline

from extensions import initialize

connected = connect_db_to_ckline()
if not connected:
    raise Exception("Cannot Connect to CKLINE! Check server status or value of config/config.ini.")
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

initialize()
# add route
app.include_router(chatbot_router)
app.include_router(chatroom_router)


@app.route("/")
async def main():
    return {"status": "ok"}


if __name__ == "__main__":
    if debug:
        # for debug. if not debug - run uvicorn on cmd.
        import uvicorn
        uvicorn.run(app,
                    host=server_config.get('SERVER', 'Host'),
                    port=server_config.getint('SERVER', 'Port'),
                    log_level=logging.DEBUG)
