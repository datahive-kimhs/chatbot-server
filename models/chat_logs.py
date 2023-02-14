from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from models.base import UUIDIdxPKBase


@dataclass
class QuestionLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_QUESTION_LOG"

    user_ip: str = Column('USER_IP', String(255))
    user_os: str = Column('USER_OS', String(255))
    user_id: str = Column('USER_ID', String(255))
    content: str = Column('CONTENT', String(4000))
    time: datetime = Column('TIME', TIMESTAMP)


@dataclass
class AnswerLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_ANSWER_LOG"

    id: str = Column('ID', String(255))
    question_idx: str = Column('QUESTION_IDX',
                               String(255),
                               ForeignKey("CKAIX_QUESTION_LOG.IDX",
                                          ondelete='CASCADE')
                               )
    content: str = Column('CONTENT', String(4000))
    time: datetime = Column('TIME', TIMESTAMP)

    question = relationship("QuestionLog")


@dataclass
class ChatLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_CHAT_LOG"

    chatroom_idx: str = Column('CHATROOM_IDX',
                               String(100),
                               ForeignKey('CKAIX_CHATROOM.IDX', ondelete='CASCADE'))
    user_ip: str = Column('USER_IP', String(255))
    user_os: str = Column('USER_OS', String(255))
    user_id: str = Column('USER_ID', String(255))
    content: str = Column('CONTENT', String(4000))
    created: datetime = Column('CREATED', TIMESTAMP)


@dataclass
class UserChatLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_USER_CHAT_LOG"

    chat_idx: str = Column('CHAT_IDX',
                           String(100),
                           ForeignKey("CKAIX_CHAT_LOG.IDX",
                                      ondelete='CASCADE')
                           )

    chat_log = relationship("ChatLog")


@dataclass
class AnswerChatLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_ANSWER_CHAT_LOG"

    chat_idx: str = Column('CHAT_IDX',
                           String(100),
                           ForeignKey("CKAIX_CHAT_LOG.IDX",
                                      ondelete='CASCADE')
                           )
    answer_id: str = Column('ANSWER_ID', String(100))

    chat_log = relationship("ChatLog")
