from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Sequence

from models.base import ORMModelBase


@dataclass
class Userdictja(ORMModelBase):
    __tablename__ = "CKAIX_USER_DICT_JA"

    userdict_seq = Sequence('USER_DICT_JA_SEQ')

    idx: int = Column('IDX', Integer, server_default=userdict_seq.next_value(), primary_key=True)
    word: str = Column('WORD', String(500))
    shape: str = Column('SHAPE', String(20))