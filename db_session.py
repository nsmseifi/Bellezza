import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import environ

db_name = environ.get('db_name')
host_name = environ.get('host_name')
host_port = environ.get('host_port')
db_username = environ.get('db_username')
db_password = environ.get('db_password')

engine_address = 'postgresql://{}:{}@{}:{}/{}'.format(
    db_username, db_password,
    host_name, host_port, db_name)
logging.debug("engine_address is : "+engine_address)

engine = create_engine(engine_address, echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()
