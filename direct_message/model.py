from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class DirectMessage(Base):

    __tablename__ = 'direct_messages'

    id = Column(UUID,nullable=False,primary_key=True)
    sender = Column(String,nullable=False)
    reciever = Column(String,nullable=False)
    message = Column(String,nullable=False)
    creation_date = Column(Integer,nullable=False)
    seen = Column(Boolean,default=False)
    modification_date = Column(Integer)
    modifier = Column(String)
