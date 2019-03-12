from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class Event(Base):

    __tablename__ = 'events'

    id = Column(UUID,nullable=False,primary_key=True)
    creator = Column(String,nullable=False)
    target = Column(String,nullable=False)
    action = Column(String,nullable=False)
    creation_date = Column(Integer,nullable=False)
    entity_name = Column(String)
    entity_id = Column(UUID)
    modification_date = Column(Integer)
    modifier = Column(String)
    seen = Column(Boolean,default=False)
