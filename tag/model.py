from sqlalchemy import Column, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(UUID, nullable=False, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    creator = Column(String,nullable=False)
    creation_date = Column(String,nullable=False)
    modification_date = Column(String)
    modifier = Column(String)
