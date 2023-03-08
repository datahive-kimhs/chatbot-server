from enum import Enum
from pydantic import BaseModel


class BotType(str, Enum):
    pass


class Languages(str, Enum):
    korean = "ko"
    english = "en"
    japanese = "ja"
    chinese = "cn"


class ChatOptions(int, Enum):
    default = 0
    exposure = 1


class ChatData(BaseModel):
    query: str
    bot_type: str | None
    lang: Languages
    opt: ChatOptions
