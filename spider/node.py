from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Node(Base):
	# Represents a single node in the crawled tree, stored in the database.
	__tablename__ = 'nodes'

	id = Column(Integer, primary_key=True, autoincrement=True)
	url = Column(String, nullable=False, unique=True)
	parent_id = Column(Integer, ForeignKey('nodes.id', ondelete="CASCADE"))
	depth = Column(Integer, nullable=False)
	searched = Column(Boolean, nullable=False)

	def __init__(self, url, parent_id=None, depth=0, searched=False):
		self.url = url
		self.parent_id = parent_id
		self.depth = depth
		self.searched = searched
