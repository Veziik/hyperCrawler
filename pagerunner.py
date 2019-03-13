from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlparse
from urllib.error import URLError
from link_finder import LinkFinder
from time import gmtime, strftime, sleep
import threading
from domain import *
import queue

class Pagerunner:

	startAddress = ''					#The starting Address for the search
	domains = set()	#	#	#	#	#	#Domains that the runner is allowed to traverse
	visited = set()						#Addresses tnat the runner has visited
	notvisited = queue.Queue()	#	#	#Adressses that the runner has not yet visited
	visitedLock = threading.RLock()		#Threading Lock for adding to the visited list
	notvisitedLock = threading.RLock()	#Threading Lock for adding to the queue
	tabooWords = set()					#Keywords that ban links from being searched by the runner
	debugOn = False		#	#	#	#	#Enables/Disables debug text 
	verboseOn = False					#Enables/Disables verbose text (less detailed than debug text)
	function = None		#	#	#	#	#function that the Pagerunner uses on each page 
	threads = set()						#List of the threads in use 
										#Next Line is the headers the runner uses when sending a request
	headers = {'Connection' : 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',}

	def __init__(self, newStartAddress=None, newDomains=None, newTabooWords=[], newDebugOn=False, newVerboseOn = False,  newThreadCount = 1):
		if not Pagerunner.startAddress:
			Pagerunner.startAddress = newStartAddress
		
		Pagerunner.addLink(newStartAddress)
		
		if newDomains:
			Pagerunner.domains.add(newDomains) 
		
		if newTabooWords:
			Pagerunner.tabooWords.add(newTabooWords)
		
		if newDebugOn:
			Pagerunner.debugOn = newDebugOn

		if newVerboseOn:
			Pagerunner.verboseOn = newVerboseOn
		
		if Pagerunner.debugOn:	print('creating main thread')
		Pagerunner.crawlPage(Pagerunner.nextLink())

		if Pagerunner.debugOn:	print('creating child threads')
		Pagerunner.createThreads(newThreadCount)

		if Pagerunner.debugOn:	print('starting child threads')
		Pagerunner.start()
		
		
	@staticmethod
	def work():
		while True:
			Pagerunner.crawlPage(Pagerunner.nextLink())

	@staticmethod
	def start():
		for thread in Pagerunner.threads:
			if Pagerunner.debugOn:	print('starting ' + thread.name)
			
			thread.run()

	@staticmethod
	def toggleDebug():
		Pagerunner.debug = not Pagerunner.debug

	@staticmethod
	def createThreads(newThreadCount):
		print('ThreadCount: ' + str(newThreadCount))
		i = 0
		while i < newThreadCount:
			name = 'Thread ' + str(i)
			print('i: ' + str(i))
			print('creating ' + name)
			t = threading.Thread(target=Pagerunner.work)
			t.name = name
			t.daemon = True
			Pagerunner.threads.add(t)
			i+=1
			

	@staticmethod
	def addDomains(newDomains):
		Pagerunner.domains.add(newDomains)

	@staticmethod
	def addTabooWords(newTabooWords):
		Pagerunner.tabooWords.add(newTabooWords)

	@staticmethod
	def removeDomains(oldDomains):
		Pagerunner.domains.remove(oldDomains)

	@staticmethod
	def removeTabooWords(oldTaboowords):
		Pagerunner.tabooWords.remove(oldTaboowords)

	@staticmethod
	def queueEmpty():
		return Pagerunner.notvisited.empty()

	@staticmethod
	def addLink(newLink):
		with Pagerunner.notvisitedLock:
			Pagerunner.notvisited.put(newLink)

	@staticmethod
	def addLinks(newLinks):
		with Pagerunner.notvisitedLock:
			for  link in newLinks:
				Pagerunner.addLink(link)

	@staticmethod
	def nextLink():
		nextLink = None
		counter = 1
		with Pagerunner.notvisitedLock:
			nextLink =Pagerunner.notvisited.get(False)
		return nextLink

	@staticmethod		
	def crawlPage(pageUrl):
		forbidden = True 

		if get_domain_name(pageUrl) in Pagerunner.domains:
			forbidden = False

		for taboo in Pagerunner.tabooWords:
			forbidden = forbidden or (taboo in pageUrl)

		if pageUrl not in Pagerunner.visited and not forbidden:
			if Pagerunner.debugOn or Pagerunner.verboseOn:
				print(threading.current_thread().name + ' crawling ' + pageUrl )
			if Pagerunner.debugOn:
				print('''Data structure Status:
	visited: ''' + str(Pagerunner.visited) + ''' 
					
	domains: ''' + str(Pagerunner.domains) + '''
					
	notVisited: ''' + str(Pagerunner.notvisited.qsize()) + '''

	threads: ''' + str(Pagerunner.threads) )
			Pagerunner.addLinks(Pagerunner.gatherLinks(pageUrl))


	@staticmethod
	def gatherLinks(pageUrl):
		htmlText = ''
		returnlinks = set()
		try:	
			request=Request(pageUrl,None,Pagerunner.headers) #The assembled request
			response = urlopen(request)
			returnheader = response.getheader('Content-Type')	
			htmlBytes = response.read()
			
			if 'text/html' in returnheader:
			
				htmlText = htmlBytes.decode("utf-8")
				finder = LinkFinder(Pagerunner.startAddress, pageUrl)
				finder.feed(htmlText)
				foundlinks = finder.page_links() 
				returnlinks = foundlinks
				#print(returnlinks)
			Pagerunner.useFunctionOnEachPage(response)

			response.close()
			Pagerunner.visited.add(pageUrl)
		
		except URLError:
			print('error encountered, most likely a 404\n')
			return set()			
		return returnlinks 

	

	@staticmethod
	def useFunctionOnEachPage(response):
			pass
		
