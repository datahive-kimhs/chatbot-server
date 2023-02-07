from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Sequence

from models.base import ORMModelBase


@dataclass
class Scenarioja(ORMModelBase):
    __tablename__ = "CKAIX_SCENARIO_JA"

    senario_seq = Sequence('SCENARIO_JA_SEQ')

    index: int = Column('IDX', Integer, server_default=senario_seq.next_value(), primary_key=True)
    depth: int = Column('DEPTH', Integer)
    parent_idx: int = Column('PARENT_IDX', Integer)
    ner: str = Column('NER', String(500))
    question: str = Column('QUESTION', String(500))
    answer: str = Column('ANSWER', String(500))
    keyword_answer: str = Column('KEYWORD_ANSWER', String(500))
    url: str = Column('URL', String(500))
    category: int = Column('CATEGORY', Integer)
    priority: int = Column('PRIORITY', Integer)
    exposure: str = Column('EXPOSURE', String(20))
    usruse: str = Column('USRUSE', String(20))
    ner_en: str = Column('NER_EN', String(500))
    question_en: str = Column('QUESTION_EN', String(500))
    answer_en: str = Column('ANSWER_EN', String(500))
    keyword_answer_en: str = Column('KEYWORD_ANSWER_EN', String(500))
    url_en: str = Column('URL_EN', String(500))
    ner_ja: str = Column('NER_JA', String(500))
    question_ja: str = Column('QUESTION_JA', String(500))
    answer_ja: str = Column('ANSWER_JA', String(500))
    keyword_answer_ja: str = Column('KEYWORD_ANSWER_JA', String(500))
    url_ja: str = Column('URL_JA', String(500))
    ner_cn: str = Column('NER_CN', String(500))
    question_cn: str = Column('QUESTION_CN', String(500))
    answer_cn: str = Column('ANSWER_CN', String(500))
    keyword_answer_cn: str = Column('KEYWORD_ANSWER_CN', String(500))
    url_cn: str = Column('URL_CN', String(500))
