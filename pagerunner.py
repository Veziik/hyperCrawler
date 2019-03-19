from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlparse
from urllib.error import URLError
from link_finder import LinkFinder
from time import gmtime, strftime, sleep
import threading
from domain import *
import queue


class DoNothing(object):
	
	def __init__(self):
		pass
	
	def pipe(self, pageUrl,response, isLastRun):
		if Pagerunner.debugOn or Pagerunner.verboseOn:
			print(threading.current_thread().name + ' doing nothing with the given page')
		




class Pagerunner:

	startAddress = ''					#The starting Address for the search
	processed = set()					#domains that the function thread has processed
	domains = set()	#	#	#	#	#	#Domains that the runner is allowed to traverse
	visited = set()						#Addresses tnat the runner has visited
	notvisited = queue.Queue()	#	#	#Adressses that the runner has not yet visited
	responses = queue.Queue()			#responses that have yet to be processed
	responseLock = threading.RLock()	#	#Threading Lock for adding to the responses queue
	visitedLock = threading.RLock()	#	#Threading Lock for adding to the visited list
	notvisitedLock = threading.RLock()	#Threading Lock for adding to the queue
	tabooWords = set()					#Keywords that ban links from being searched by the runner
	debugOn = False		#	#	#	#	#Enables/Disables debug text 
	verboseOn = False					#Enables/Disables verbose text (less detailed than debug text)
	module = None		#	#	#	#	#class which the pagerunner uses to perform actions on each page 
	threads = set()						#List of the threads in use 
										#Next Line is the headers the runner uses when sending a request
	headers = {'Connection' : 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',}


	def __init__(self, newStartAddress=None, newDomains=None, newTabooWords=None, newDebugOn=False, newVerboseOn = False,  newThreadCount = 1, newModule=DoNothing() ):
		if not Pagerunner.startAddress:
			Pagerunner.startAddress = newStartAddress
		
		Pagerunner.addLink(newStartAddress)
		
		if newDomains:
			for domain in newDomains:
				Pagerunner.domains.add(domain) 
		
		if newTabooWords:
			for taboo in newTabooWords:
				Pagerunner.tabooWords.add(taboo)
		
		if newDebugOn:
			Pagerunner.debugOn = newDebugOn

		if newVerboseOn:
			Pagerunner.verboseOn = newVerboseOn
		
		if newModule:
			Pagerunner.module = newModule
		else:
			Pagerunner.module = DoNothing.doNothing

		if Pagerunner.debugOn:
				print('''Data structure Status on init:
	visited: ''' + str(Pagerunner.visited) + ''' 
					
	domains: ''' + str(Pagerunner.domains) + '''
					
	notVisited: ''' + str(Pagerunner.notvisited.qsize()) + '''

	threads: ''' + str(Pagerunner.threads) )


		if Pagerunner.debugOn:	
			print('starting init process')
		Pagerunner.crawlPage(Pagerunner.nextLink())



		if Pagerunner.debugOn:	
			print('creating child threads')
		Pagerunner.createThreads(newThreadCount)
		

		if Pagerunner.debugOn:	
			print('starting child threads')
		Pagerunner.startThreads()
		

	@staticmethod
	def work():
		while not Pagerunner.notVisitedIsEmpty():
			Pagerunner.crawlPage(Pagerunner.nextLink())

	@staticmethod
	def startThreads():
		for thread in Pagerunner.threads:
			if Pagerunner.debugOn or Pagerunner.verboseOn:	
				print('starting ' + thread.name)
			thread.start()

	@staticmethod
	def toggleDebug():
		Pagerunner.debug = not Pagerunner.debug

	@staticmethod
	def createThreads(newThreadCount):
		if Pagerunner.debugOn:
			print('Thread count: ' + str(newThreadCount) + ' +1 function thread')
		i = 0
		while i < newThreadCount:
			name = 'Crawler ' + str(i)
			#print('i: ' + str(i))
			if Pagerunner.debugOn or Pagerunner.verboseOn:
				print('creating ' + name)
			t = threading.Thread(target=Pagerunner.work)
			t.name = name
			#t.daemon = True
			Pagerunner.threads.add(t)
			i+=1

		if Pagerunner.debugOn or Pagerunner.verboseOn:
			print('creating Function Thread')
		
		t = threading.Thread(target=Pagerunner.functionThreadWork)
		t.name = 'Function Thread'
		Pagerunner.threads.add(t)

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
	def notVisitedIsEmpty():
		with Pagerunner.notvisitedLock:
			return Pagerunner.notvisited.empty()
	
	@staticmethod
	def responsesIsEmpty():
		with Pagerunner.responseLock:
			return Pagerunner.responses.empty()

	@staticmethod
	def addLink(newLink):
		with Pagerunner.notvisitedLock:
			Pagerunner.notvisited.put(newLink)

	@staticmethod
	def addLinks(newLinks):
		with Pagerunner.notvisitedLock:
			for  newLink in newLinks:
				Pagerunner.notvisited.put(newLink)
	
	@staticmethod
	def pageVisited(pageUrl):	
		with Pagerunner.visitedLock:
			return pageUrl in Pagerunner.visited
		

	@staticmethod
	def addResponse(response):
		with Pagerunner.responseLock:
			Pagerunner.responses.put(response)

	@staticmethod
	def nextLink():
		nextLink = None
		counter = 1
		with Pagerunner.notvisitedLock:
			nextLink =Pagerunner.notvisited.get(False)
		return nextLink

	@staticmethod		
	def crawlPage(pageUrl):
		if Pagerunner.debugOn or Pagerunner.verboseOn:
				print(threading.current_thread().name + ' crawling ' + pageUrl )

		if Pagerunner.debugOn:
				print('''Data structure Status:
	visited: ''' + str(Pagerunner.visited) + ''' 
					
	domains: ''' + str(Pagerunner.domains) + '''

	taboos: ''' + str(Pagerunner.tabooWords) + '''
					
	notVisited: ''' + str(Pagerunner.notvisited.qsize()) + '''

	threads: ''' + str(Pagerunner.threads) )


		forbidden = True 
		if get_domain_name(pageUrl) in Pagerunner.domains:
			forbidden = False

		for taboo in Pagerunner.tabooWords:
			forbidden = forbidden or (taboo in pageUrl)

		if  (not Pagerunner.pageVisited(pageUrl)) and (not forbidden):			
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
			Pagerunner.addResponse((pageUrl, response))

			if 'text/html' in returnheader:
			
				htmlText = htmlBytes.decode('utf-8')
				finder = LinkFinder(Pagerunner.startAddress, pageUrl)
				finder.feed(htmlText)
				foundlinks = finder.page_links() 
				returnlinks = foundlinks
				#print(returnlinks)
			

			response.close()

			Pagerunner.visited.add(pageUrl)
		
		except URLError as e:
			print(e)
			return set()
		except UnicodeDecodeError as e:
			print(e)
			return set()
		except UnicodeDecodeError as e:
			print(e)
			return set()
		finally:
			Pagerunner.visited.add(pageUrl)

		return returnlinks 

	

	@staticmethod
	def functionThreadWork():
		while (not Pagerunner.notVisitedIsEmpty()) or (not Pagerunner.responsesIsEmpty()):

			if not Pagerunner.responsesIsEmpty():
				
				if Pagerunner.debugOn:
					print('Function Thread executing')
			
				(pageUrl, response) = Pagerunner.responses.get(False)
				if pageUrl not in Pagerunner.processed:
					Pagerunner.module.pipe( pageUrl,response,isLastRun=False)
					Pagerunner.processed.add(pageUrl)
		
		


		Pagerunner.module.pipe( None,None,isLastRun=True)
