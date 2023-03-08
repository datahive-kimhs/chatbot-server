from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, TIMESTAMP, Integer

from models.base import UUIDIdxPKBase


class RoomStatus(Enum):
    """
    define Room Status.
    NONE = Chatroom does not exist in DB(chatroom table).
    OPEN = Chatroom is open.
    CLOSE = Chatroom is closed.
    WAIT = Chatroom is staying.
    """
    NONE: int = 0
    OPEN: int = 1
    CLOSE: int = 2
    WAIT: int = 3
    ETC: int = 4


@dataclass
class ChatRoom(UUIDIdxPKBase):
    """
    Careful! - dataclasses.asdict(ChatRoom instance) return RoomStatus instance, not int.
    Can be use keyword argument 'dict_factory' of 'dataclasses.asdict' function.
    You can use function 'utils.asdict_enum_to_value' for that.
    """
    __tablename__ = "CKAIX_CHATROOM"

    status: RoomStatus = Column('STATUS', Integer)
    created: datetime = Column('CREATED', TIMESTAMP)
    updated: datetime = Column('UPDATED', TIMESTAMP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

