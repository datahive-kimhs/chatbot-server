from dataclasses import dataclass

from sqlalchemy import Column, String, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base


# 기본 스키마가 CKAIX가 아니므로 별도로 지정함.
ORMModelBase = declarative_base(name='CKAIX',
                                metadata=MetaData(schema="CKAIX"))


@dataclass
class UUIDIdxPKBase(ORMModelBase):
    __abstract__ = True

    idx: str = Column('IDX', String(100), primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
