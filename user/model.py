from sqlalchemy import String, Column, Integer
from sqlalchemy.dialects.postgresql import UUID
from db_session import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    creator = Column(String, nullable=False)
    creation_date = Column(Integer, nullable=False)
    modification_date = Column(Integer)
    modifier = Column(String)


