from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def get_engine(db_path):
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	return engine

def init_db(engine):
	Base.metadata.create_all(engine)


