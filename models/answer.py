from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Sequence

from models.base import ORMModelBase


@dataclass
class Answer(ORMModelBase):
    __tablename__ = "CKAIX_ANSWER"

    answer_seq = Sequence('ANSWER_SEQ')

    idx: int = Column('IDX', Integer, server_default=answer_seq.next_value(), primary_key=True)
    ner: str = Column('NER', String(500))
    answer: str = Column('ANSWER', String(1000))
    url: str = Column('URL', String(500))
    exposure: str = Column('EXPOSURE', String(20))
