from dataclasses import dataclass

from sqlalchemy import Column, String, Integer, CHAR

from models.base import ORMModelBase


@dataclass
class BulkPerFor(ORMModelBase):
    __tablename__ = "CKAIX_BULKPERFOR"

    outyer: str = Column('OUTYER', String(16))
    outmon: str = Column('OUTMON', String(8))
    outsls: str = Column('OUTSLS', CHAR(1))
    outpol: str = Column('OUTPOL', String(5))

    outrtn: int = Column('OUTRTN', Integer)
    outusd: int = Column('OUTUSD', Integer)
    outopb: int = Column('OUTOPB', Integer)

    outstm: str = Column('OUTSTM', String(16))

