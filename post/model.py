from sqlalchemy import Column, String, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String)
    likes = Column(Integer)
    creator = Column(String, nullable=False)
    creation_date = Column(Integer, nullable=False)
    modification_date = Column(Integer)
    modifier = Column(String)
    pictures_id = Column(ARRAY(String))
    category = Column(ARRAY(String), nullable=False)
    tags = Column(ARRAY(String))
#
#
# class PostPicture(Base, Image):
#     __tablename__ = 'post_pictures'
#     post_id = Column(Integer, ForeignKey('post.id'), primary_key=True)
#     post = relationship('Post')
#
