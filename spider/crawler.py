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
		self.tree.add_batch(links, parent_url)

	def prep_search(self):
		next_floor = deque()
		leaves = self.tree.get_not_searched()
		
		if len(leaves) == 1:
			floor = [next(iter(leaves)).url]
		else:
			leaves_by_depth = sorted(leaves, key=lambda leaf: leaf.depth)
			floor = deque()
			for leaf in leaves_by_depth:
				if leaf.searched == False:
					floor.append(leaf.url)
			
		logger.info("Search stage 1 complete")
		print("Search stage 1 complete")
		return floor, next_floor

	def search(self, depth, check_adds):
		
		floor, next_floor = self.prep_search()
			
		for d in range(depth):
			responses = request_batch(floor)
			for index, child in responses:
				
				child_url = floor[index]
				childs = fetch_links(child_url, child)
				if check_adds: 
					all_nodes1 = len(self.tree.all_nodes())
					self.add_children(childs, child_url)
					self.tree.set_searched(child_url, True)
					all_nodes2 = len(self.tree.all_nodes())
					print(f"Completed: {child_url}\nLinks added: {all_nodes2-all_nodes1}")
				else:
					self.add_children(childs, child_url)
					self.tree.set_searched(child_url, True)
					print(f"Completed: {child_url}")
				next_floor.extend(childs)
				
			floor = next_floor
			next_floor = deque()
			
	def generate_report(self):
		
		self.report = ""
		self.report += f"Links found: {len(self.tree.all_nodes())-1}\n"
		self.report += f"Max Depth: {self.tree.max_depth()}"
		
		print(self.report)

	def save_tree(self, filename):
		open(filename,'w').close()
		with open(filename, "a") as f:
			f.writelines([node.url+"\n" for node in self.tree.all_nodes()])

	def crawl(self, depth, check_adds=True):
		try:
			self.search(depth, check_adds)
			logger.info("Crawl complete")
			print("Crawl complete")
		except KeyboardInterrupt:
			print("You ended the crawl.")
			logger.info("You ended the crawl.\n")
		#except Exception as e:
			#logger.critical(f'Fatal error occured. Error: -->  {e}  <--')
			#print(f'Fatal error occured. Error: -->  {e}  <--')
