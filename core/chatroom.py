import uuid
import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session
from fastapi.logger import logger as app_logger

from models.chatroom import ChatRoom, RoomStatus
from core.exc import CannotFoundData
from connection import get_ckline_db_engine


def get_chatroom(session: Session, room_id: str) -> ChatRoom | None:
    """
    return ChatRoom object. if not found, return None.
    :param session:
    :param room_id:
    :return:
    """
    return session.get(ChatRoom, room_id)


def get_room_status(session: Session, room_id: str) -> RoomStatus:
    room_info = get_chatroom(session, room_id)
    if room_info is None:
        return RoomStatus.NONE
    if room_info.status != RoomStatus.OPEN:
        return False
    return True


def update_chatroom_status(session: Session, room_id: str, status: RoomStatus) -> str | None:
    if session.get(ChatRoom, room_id) is None:
        return None
    stmt = update(ChatRoom).where(ChatRoom.idx == room_id).values(status=status).returning(ChatRoom.idx.label('idx'))
    result = session.execute(stmt).one()
    if result is None or result.idx != room_id:
        raise CannotFoundData("Something wrong update row in DB (Cannot found index)",
                              f"- {ChatRoom.__tablename__}.{room_id}...")
    return result.idx


def create_chatroom(session: Session) -> str | None:
    new_room_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        new_room = ChatRoom(idx=new_room_id,
                            created=now,
                            updated=now,
                            status=RoomStatus.WAIT)
        session.add(new_room)
        return new_room_id
    except Exception as e:
        app_logger.exception(e)
        return None


def close_chatroom(session: Session, room_id: str):
    closed_room_idx = update_chatroom_status(session=session, room_id=room_id, status=RoomStatus.CLOSE)
    if closed_room_idx != room_id:
        raise
    pass


def init_chatroom(room_id: str = None) -> None:
    ckline_db = get_ckline_db_engine()
    with ckline_db.get_db_session() as session:
        status = get_room_status(room_id=room_id)
        if status == RoomStatus.NONE or status == RoomStatus.CLOSE:
            pass
        elif status == RoomStatus.WAIT:
            pass
        elif status == RoomStatus.OPEN:
            pass
        else:
            pass
    return
