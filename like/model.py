from sqlalchemy import Column, String, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class Like(Base):
    __tablename__ = 'likes'
    id = Column(UUID,nullable=False,primary_key=True)
    post_id = Column(UUID,nullable=False)
    creator = Column(String,nullable=False)
    creation_date = Column(Integer,nullable=False)
