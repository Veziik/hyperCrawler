from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlparse
from urllib.error import URLError
from link_finder import LinkFinder
from threading import RLock, current_thread
from time import gmtime, strftime
from domain import *
import queue

class Pagerunner:

	startAddress = ''			#The starting Address for the search
	domains = set()				#Domains that the runner is allowed to traverse
	visited = set()				#Addresses tnat the runner has visited
	notvisited = queue.Queue()	#Adressses that the runner has not yet visited
	visitedLock = RLock()		#Threading Lock for adding to the visited list
	notvisitedLock = RLock()	#Threading Lock for adding to the queue
	tabooWords = set()			#Keywords that ban links from being searched by the runner
	debugOn = False				#Enables/Disables debug text #Next Line is the headers the runner uses when sending a request
	function = None
	headers = {'Connection' : 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',}

	def __init__(self, newStartAddress=None, newDomains=None, newTabooWords=None, newDebugOn=None ):
		if newStartAddress and Pagerunner.notvisited.empty():
			Pagerunner.startAddress = newStartAddress
			Pagerunner.addLink(newStartAddress)
		elif newStartAddress and not queue.empty():
			Pagerunner.addLink(newStartAddress)
		if newDomains:
			Pagerunner.domains.add(newDomains) 
		if newTabooWords:
			Pagerunner.tabooWords.add(newTabooWords)
		if newDebugOn:
			Pagerunner.debugOn = newDebugOn
		
	@staticmethod
	def work(threadName):
		while not Pagerunner.queueEmpty():
			Pagerunner.crawlPage(threadName, Pagerunner.nextLink())


	@staticmethod
	def toggleDebug():
		Pagerunner.debug = not Pagerunner.debug


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
		with Pagerunner.notvisitedLock:
			nextLink =Pagerunner.notvisited.get()
		if nextLink:
			return nextLink
		else :
			if debugOn:
				print('no more links, exiting')
			exit(0)


	@staticmethod		
	def crawlPage(threadName, pageUrl):
		forbidden = True

		for domain in Pagerunner.domains:
			forbidden = forbidden and (domain not in pageUrl)

		for taboo in Pagerunner.tabooWords:
			forbidden = forbidden or (taboo in pageUrl)

		if pageUrl not in Pagerunner.visited and not forbidden:
			if Pagerunner.debugOn:
				print(threadName + ' crawling ' + pageUrl )
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

			Pagerunner.useFunctionOnEachPage(response)

			response.close()
		
		except URLError:
			print('error encountered, most likely a 404\n')
			return set()			
		return returnlinks 

	@staticmethod
	def useFunctionOnEachPage(response):
			pass
		
