from dataclasses import dataclass

from sqlalchemy import Column, String, DATE

from models.base import ORMModelBase


@dataclass
class AccessLog(ORMModelBase):
    __tablename__ = "CKAIX_ACCESS_LOG"

    id: str = Column('ID', String(30))
    ip: str = Column('IP', String(20))
    dt: str = Column('DT', DATE)
    # service value C: Chatbot, D: Dashboard
    service: str = Column('SERVICE', String(1))
    s_menu: str = Column('S_MENU', String(10))
