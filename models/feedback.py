from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base import UUIDIdxPKBase


@dataclass
class FeedbackLog(UUIDIdxPKBase):
    __tablename__ = "CKAIX_FEEDBACK_LOG"

    answer_idx: str = Column('ANSWER_IDX',
                             String(255),
                             ForeignKey("CKAIX_ANSWER_LOG.IDX")
                             )
    question_idx: str = Column('QUESTION_IDX',
                               String(255),
                               ForeignKey("CKAIX_QUESTION_LOG.IDX")
                               )
    category_idx: str = Column('FEEDBACK_CATEGORY_IDX',
                               String(255),
                               ForeignKey("CKAIX_FEEDBACK_CATEGORY.IDX")
                               )
    user_id: str = Column('USER_ID', String(255))
    time: datetime = Column('TIME', TIMESTAMP)

    question = relationship("QuestionLog")
    answer = relationship("AnswerLog")
    feedback_category = relationship("FeedbackCategory")
    user_input = relationship("FeedbackLogUserInput", uselist=False)


@dataclass
class FeedbackCategory(UUIDIdxPKBase):
    __tablename__ = "CKAIX_FEEDBACK_CATEGORY"

    category: str = Column('CATEGORY', String(255))
    etc: str = Column('ETC', String(255))


@dataclass
class FeedbackLogUserInput(UUIDIdxPKBase):
    __tablename__ = "CKAIX_FEEDBACK_LOG_USER_INPUT"

    feedback_log_idx: str = Column('FEEDBACK_LOG_IDX',
                                   String(255),
                                   ForeignKey("CKAIX_FEEDBACK_LOG.IDX", ondelete=True)
                                   )
    content: str = Column('CONTENT', String(4000))
    created: datetime = Column('CREATED', TIMESTAMP)

    feedback_log = relationship("FeedbackLog",
                                back_populates="user_input")
