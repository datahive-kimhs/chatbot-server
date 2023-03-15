from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Sequence

from models.base import ORMModelBase


@dataclass
class InputTemplate(ORMModelBase):
    __tablename__ = "CKAIX_INPUT_TEMPLATE"

    input_seq = Sequence('INPUT_SEQ')

    idx: int = Column('IDX', Integer, server_default=input_seq.next_value(), primary_key=True)
    name: str = Column('NAME', String(100))
    name_en: str = Column('NAME_EN', String(100))
    name_ja: str = Column('NAME_JA', String(100))
    name_cn: str = Column('NAME_CN', String(100))
    table_name: str = Column('TABLE_NAME', String(100))
