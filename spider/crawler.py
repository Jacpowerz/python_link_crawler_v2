from .tree import Tree
import re
from collections import deque
from .request_utils import logger, fetch_links, request_batch

class Crawler:
	
	def __init__(self, seed, db_path, new_tree):
		if seed[-1] == "/": seed = seed[:-1]
		self.seed = seed
		self.tree = Tree(db_path)
		if new_tree:
			self.tree.clear_data()
			self.tree.add_root(seed)
		self.report = "NO DATA"

	def add_children(self, links, parent_url):
		for link in links:
			self.tree.add_node(url=link, parent_url=parent_url)
	
	def search_stage1(self):
		leaves = deque(node for node in self.tree.get_leaves())
		
		if len(leaves) == 1:
			floor = [next(iter(leaves)).url]
			next_floor = deque()
		else:
			min_depth = min([self.tree.get_depth(leaf.url) for leaf in leaves])
			floor = deque(node.url for node in leaves if self.tree.get_depth(node.url)==min_depth)
			next_floor = deque(node.url for node in leaves if self.tree.get_depth(node.url)==min_depth+1)
		logger.info("Search stage 1 complete")
		print("Search stage 1 complete")
		return floor, next_floor
		
	def search(self, depth):
		
		floor, next_floor = self.search_stage1()
			
		for d in range(depth):
			responses = request_batch(floor)
			for index, child in responses:
				child_url = floor[index]
				try:
					childs = fetch_links(child_url, child)
					self.add_children(childs, child_url)
					next_floor.extend(childs)
				except Exception as e:
					logger.error("Error: {e}")
				
				print(f"Completed: {child_url}\nLinks added: {len(childs)}")
				
			floor = next_floor
			next_floor = deque()
			
	def generate_report(self):
		
		self.report = ""
		self.report += f"Links found: {len(self.tree.all_nodes())-1}\n"
		self.report += f"Max Depth: {self.tree.max_depth()}"
		
		print(self.report)

	def save_tree(self, filename): 
		for node in self.tree.all_nodes():
			f = open(filename, "a")
			f.write(node.url+"\n")
			f.close()

	def crawl(self, depth):
		try:
			self.search(depth)
			logger.info("Crawl complete")
			print("Crawl complete")
		except KeyboardInterrupt:
			print("You ended the crawl.")
			logger.info("You ended the crawl.\n")
		except Exception as e:
			logger.critical(f'Fatal error occured. Error: -->  {e}  <--')
			print(f'Fatal error occured. Error: -->  {e}  <--')
