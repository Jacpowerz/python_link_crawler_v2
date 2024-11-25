# Fix grequests w/ silenced warning
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
create_urllib3_context()

import grequests
from bs4 import BeautifulSoup
import re
import logging

import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (100_000, 100_000))	

logger = logging.getLogger(__name__)
logging.basicConfig(filename='crawler.log', filemode='w', encoding='utf-8', level=logging.INFO)

https_regex = re.compile(r"^https?://")
relative_regex = re.compile(r"^/")

def exception_handler(request, exception):
	logger.error(f'grequests error occured. Error: -->  {exception}  <--')
	
def fetch_links(url, response):
	try:
		soup = BeautifulSoup(response.text, 'html.parser')
		a_tags = soup.find_all('a')
		links = set()
			
		for tag in a_tags:
			link = tag.get('href')
			if link:
				if link[-1] == "/": link = link[:-1]
				if https_regex.match(link):
					links.add(link)
				elif relative_regex.match(link):
					links.add(url + link)
		return links
	except AttributeError as e:
		logger.error(e)

def request_batch(batch):
	pending = (grequests.get(u) for u in batch)
	responses = grequests.imap_enumerated(pending, exception_handler=exception_handler)
	return responses
