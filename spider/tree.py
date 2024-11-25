from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import not_
from sqlalchemy import update
from .database import get_engine, init_db
from .node import Node
from .exceptions import DatabaseError
from .request_utils import logger

class Tree:
	def __init__(self, db_path):
		# Initializes the tree object and sets up the database engine and session
		self.engine = get_engine(db_path)
		Node.metadata.create_all(self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def get_root(self):
		session = self.Session()
		root = session.query(Node).filter_by(id=1).first()
		session.close()
		return root
		
	def get_node(self, url):
		session = self.Session()
		node = session.query(Node).filter_by(url=url).first()
		session.close()
		return node
		
	def get_node_by_id(self, id):
		session = self.Session()
		node = session.query(Node).filter_by(id=id).first()
		session.close()
		return node
		
	def add_root(self, url):
		# Adds a root node directly to the database.
		try:
			node = Node(url=url, parent_id=None)
			session = self.Session()
			session.add(node)
			session.commit()
		except IntegrityError:
			session.rollback()
			logger.info(f"Node for {url} already exists in the database.")
		finally:
			session.close()
		
	def add_node(self, url, parent_url):
		# Adds a new node directly to the database.
		try:
			parent = self.get_node(parent_url)
			if parent:
				node = Node(url=url, parent_id=parent.id, depth=self.get_depth(parent_url)+1)
			else:
				raise ValueError
			session = self.Session()
			session.add(node)
			session.commit()
		except IntegrityError:
			session.rollback()
			logger.info(f"Node for {url} already exists in the database.")
		except ValueError:
			session.rollback()
			raise DatabaseError(f"Parent node: {parent_url} does not exist.")
		finally:
			session.close()

	def add_batch(self, urls, parent_url):
		nodes = []
		all_urls = [node.url for node in self.all_nodes()]
		for url in urls:
			parent = self.get_node(parent_url)
			if url not in all_urls:
				nodes.append(Node(url=url, parent_id=parent.id, depth=self.get_depth(parent_url)+1))
		try:
			session = self.Session()
			session.bulk_save_objects(nodes)
			session.commit()
		except IntegrityError:
			session.rollback()
			logger.error(f"One (or more) of the urls already exists in the database.")
		except ValueError:
			session.rollback()
			logger.error(f"Parent node: {parent_url} does not exist.")
			raise DatabaseError(f"Parent node: {parent_url} does not exist.")
		finally:
			session.close()
				
	def delete_node(self, url):
		
		try:
			# Find the node instance with the given URL
			node = self.get_node(url)
			# Check if the node exists
			session = self.Session()
			if node:
				session.delete(node)  # Delete the node instance
				session.commit()  # Commit the transaction to apply the delete
			else:
				raise DatabaseError(f"Node: {url} not found")
		except Exception as e:
			session.rollback()
			raise DatabaseError("Could not delete node")
		finally:
			session.close()

	def get_children(self, url):
		node_id = self.get_node(url).id
		children = self.Session().query(Node).filter_by(parent_id=node_id)
		return children
		
	def get_parent(self, url):
		node = self.get_node(url)
		parent_id = node.parent_id
		parent = self.get_node_by_id(parent_id)
		return parent
		
	def clear_data(self):
		session = self.Session()
		try:
			# Delete all rows in all tables without dropping the schema
			for table in Node.metadata.sorted_tables:
				session.execute(table.delete())
			session.commit()  # Commit the transaction to apply the deletes
		except Exception as e:
			session.rollback()
			raise DatabaseError("Couldn't clear database")
		finally:
			session.close()

	def contains_node(self, url):
		node = self.get_node(url)
		if node:
			return True
		return False

	def get_depth(self, url):
		depth = 0
		cur_node = self.get_node(url)
		while self.get_parent(cur_node.url) != None:
			depth += 1
			cur_node = self.get_parent(cur_node.url)
		return depth
		
	def get_leaves(self):
		session = self.Session()
		# Query to find all nodes where the id is not referenced in as a parent_id anywhere
		leaves = session.query(Node).filter(
			~Node.id.in_(session.query(Node.parent_id).filter(Node.parent_id.isnot(None)))
		).all()
		session.close()
		return leaves
		
	def max_depth(self):
		return max([node.depth for node in self.all_nodes()])
		
	def size(self):
		session = self.Session()
		size = len(session.query(Node).all())
		session.close()
		return size
		
	def all_nodes(self):
		session = self.Session()
		nodes = session.query(Node).all()
		session.close()
		return nodes

	def set_searched(self, url, val):
		session = self.Session()
		session.query(Node).filter(Node.url == url).update(
                {Node.searched: val}, synchronize_session='fetch'
            )
		session.commit()
		session.close()
		
	def get_searched_val(self, url):
		node = self.get_node(url)
		return node.searched
		
	def get_not_searched(self):
		session = self.Session()
		nodes = session.query(Node).filter(Node.searched == False).all()
		session.close()
		return nodes
