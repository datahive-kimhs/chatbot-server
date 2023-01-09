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
                                          ondelete=True)
                               )
    content: str = Column('CONTENT', String(4000))
    time: datetime = Column('TIME', TIMESTAMP)

    question = relationship("QuestionLog")
