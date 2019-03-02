from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID,primary_key=True,nullable=False)
    message = Column(String,nullable=False)
    post_id = Column(UUID,nullable=False)
    creator = Column(String,nullable=False)
    creation_date = Column(Integer,nullable=False)