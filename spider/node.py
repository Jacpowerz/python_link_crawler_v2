from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Node(Base):
	# Represents a single node in the crawled tree, stored in the database.
	__tablename__ = 'nodes'

	id = Column(Integer, primary_key=True, autoincrement=True)
	url = Column(String, nullable=False, unique=True)
	parent_url = Column(String, ForeignKey('nodes.url', ondelete="CASCADE"))

	def __init__(self, url, parent_url=None):
		self.url = url
		self.parent_url = parent_url
