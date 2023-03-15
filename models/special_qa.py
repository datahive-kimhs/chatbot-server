from dataclasses import dataclass

from sqlalchemy import Column, String, CLOB

from models.base import ORMModelBase


@dataclass
class SpecialQA(ORMModelBase):
    __tablename__ = "CKAIX_SPECIAL_QA"

    question: str = Column('QUESTION', String(200))
    answer: str = Column('ANSWER', CLOB)
    answer_text: str = Column('ANSWER_TEXT', String(500))
    ner1: str = Column('NER1', String(100))
    ner2: str = Column('NER2', String(100))
    ner3: str = Column('NER3', String(100))
    ner4: str = Column('NER4', String(100))
    nerlen: str = Column('NERLEN', String(20))
