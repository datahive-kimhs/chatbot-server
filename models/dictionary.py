from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Sequence

from models.base import ORMModelBase


@dataclass
class Dictionary(ORMModelBase):
    __tablename__ = "CKAIX_DICTIONARY"

    dictionary_seq = Sequence('DICTIONARY_SEQ')

    idx: int = Column('IDX', Integer, server_default=dictionary_seq.next_value(), primary_key=True)
    word: str = Column('WORD', String(50))
    definition: str = Column('DEFINITION', String(2000))
