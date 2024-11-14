from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import not_
from .database import get_engine, init_db
from .node import Node
from .exceptions import DatabaseError

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
		
	def add_root(self, url):
		# Adds a root node directly to the database.
		try:
			node = Node(url=url, parent_url=None)
			session = self.Session()
			session.add(node)
			session.commit()
		except IntegrityError:
			session.rollback()
			print(f"Node for {url} already exists in the database.")
		finally:
			session.close()
		
	def add_node(self, url, parent_url):
		# Adds a new node directly to the database.
		try:
			parent = self.get_node(parent_url)
			if parent:
				node = Node(url=url, parent_url=parent_url)
			else:
				raise ValueError
			session = self.Session()
			session.add(node)
			session.commit()
		except IntegrityError:
			session.rollback()
		except ValueError:
			session.rollback()
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
		children = self.Session().query(Node).filter_by(parent_url=url)
		return children
		
	def get_parent(self, url):
		node = self.get_node(url)
		parent_url = node.parent_url
		parent = self.get_node(parent_url)
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
		# Query to find all nodes where the url is not referenced in any parent_url
		leaves = session.query(Node).filter(
			~Node.url.in_(session.query(Node.parent_url).filter(Node.parent_url.isnot(None)))
		).all()
		session.close()
		return leaves
		
	def max_depth(self):
		answer = [self.get_depth(node.url) for node in self.get_leaves()]
		return max(answer)
		
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
