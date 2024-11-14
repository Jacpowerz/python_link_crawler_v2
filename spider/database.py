from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

def get_engine(db_path):
	# db_path is desired location for tree/database --> should be 'databases'/{the_tree_name}
	# Creates and returns the database engine.
	# os.makedirs(os.path.dirname(db_path), exist_ok=True)
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	return engine

def init_db(engine):
	# Initializes the database by creating all tables.
	Base.metadata.create_all(engine)
