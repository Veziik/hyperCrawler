from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlparse
from urllib.error import URLError
from link_finder import LinkFinder
from general import * 
from sqlwriter import *
from threading import RLock
from time import gmtime, strftime
from domain import *

class Spider:

	project_name = ''
	base_url = ''
	domain_name = ''
	queue_file = ''
	file_directory = ''
	crawled_file = ''
	sql_file = ''
	databased_file = ''
	guidlock = RLock()
	queue = set()
	crawled = set()
	databased = set()
	qlock = RLock()
	taboo_words = []
	

	def __init__(self, project_name, base_url, domain_name, fd):
		Spider.project_name = project_name
		Spider.file_directory = fd
		Spider.base_url = base_url
		Spider.domain_name = domain_name
		Spider.queue_file = Spider.file_directory + '/queue.txt'
		Spider.crawled_file = Spider.file_directory + '/crawled.txt'
		Spider.databased_file =  Spider.file_directory + '/databased.txt'
		
		Spider.sql_file = Spider.file_directory + '/' + Spider.project_name + '.sql'
		Spider.sqllock = RLock()
		Spider.qlock = RLock()
		Spider.sqllock2 = RLock()
		Spider.taboo_words = ['profile', 'leaderboards', 'user']

		self.boot()
		user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
		headers = {'Connection' : 'keep-alive', 'User-Agent': user_agent,}
		request=Request(base_url,None,headers) #The assembled request
		response = urlopen(request)
		handle_sql_insert(Spider.sql_file,response, base_url, '')

		self.crawl_page('First Spider', Spider.base_url)

	@staticmethod
	def boot():
		create_project_dir(Spider.file_directory)
		create_data_files(Spider.project_name,Spider.base_url,Spider.file_directory)
		
		Spider.databased = file_to_set(Spider.databased_file)
		Spider.queue = file_to_set(Spider.queue_file)
		Spider.crawled = file_to_set(Spider.crawled_file)
		

	@staticmethod
	def crawl_page(thread_name, page_url):
		taboos = Spider.taboo_words
		forbidden = False 
		for taboo in taboos:
			forbidden = forbidden or (taboo in page_url)

		if page_url not in Spider.crawled and not forbidden:
			print(thread_name + ' crawling ' + page_url)
			print('Queue ' + str(len(Spider.queue)) + '| Crawled ' + str(len(Spider.crawled)))
			

			Spider.add_links_to_queue(Spider.gather_links(page_url))
		
		with Spider.qlock :
			Spider.queue.remove(page_url)
			Spider.crawled.add(page_url)
			Spider.update_files(page_url)


	@staticmethod
	def gather_links(page_url):
		html_string = ''
		returnlinks = set()
		

		try:	
			user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
			headers = {'Connection' : 'keep-alive', 'User-Agent': user_agent,}
			request=Request(page_url,None,headers) #The assembled request
			response = urlopen(request)
			returnheader = response.getheader('Content-Type')	
			html_bytes = response.read()
			




			if 'text/html' in returnheader:
			
				html_string = html_bytes.decode("utf-8")
				finder = LinkFinder(Spider.base_url, page_url)
				finder.feed(html_string)
				foundlinks = finder.page_links()
				#returnlinks = foundlinks
				returnlinks = Spider.cull(foundlinks, page_url, response) 
			
			response.close()
		
		except URLError:
			print('error encountered, most likely a 404\n')
			return set()			
		return returnlinks 


	@staticmethod 
	def cull(foundlinks, page_url, response):
		returnlinks  = set()
		for link in foundlinks:
			with Spider.sqllock:
				if link in Spider.databased:
					insert_HAS_from_databased_Items(Spider.sql_file,link, page_url)
				else:
					try:
						print('checking link ' + link)
						user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
						headers = {'Connection' : 'keep-alive', 'User-Agent': user_agent,}
						request=Request(link,None,headers) #The assembled request			
						lresponse =  urlopen(request) 

					
						handle_sql_insert(Spider.sql_file, lresponse, link, page_url)
						Spider.databased.add(link)
				
						if 'html' in lresponse.getheader('Content-Type'):
							returnlinks.add(link)
					
						response.close()
					
					except URLError:
						print('cannot open link ' + link)
					except UnicodeEncodeError:
						print('UnicodeEncodeError')
					
		

		return returnlinks


	@staticmethod
	def add_links_to_queue(links):
		for url in links:
			if url in Spider.queue:
				continue
			if url in Spider.crawled:
				continue
			if Spider.domain_name not in url:
				continue
			Spider.queue.add(url)

	@staticmethod
	def update_files(page_url):
		set_to_file(Spider.queue, Spider.queue_file)
		set_to_file(Spider.databased, Spider.databased_file)
		append_to_file(Spider.crawled_file, page_url)





		