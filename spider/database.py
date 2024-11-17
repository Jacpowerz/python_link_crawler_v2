from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import logging

Base = declarative_base()

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def get_engine(db_path):
	configure_logging()
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	return engine

def init_db(engine):
	Base.metadata.create_all(engine)


