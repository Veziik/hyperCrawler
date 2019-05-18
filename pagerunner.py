from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlparse
from urllib.error import URLError
from link_finder import LinkFinder
import time
import threading
from domain import *
import queue
import os 	
import sys
import inspect
import importlib

class DoNothing(object):
	count = 0
	def __init__(self):
		pass
	
	def pipe(self, pageUrl,response, isLastRun):
		#if Pagerunner.debugOn or Pagerunner.verboseOn:
			#print(threading.current_thread().name + ' doing nothing with the given page')
		print(str(DoNothing.count) + ' : ' + str(pageUrl))
		DoNothing.count = DoNothing.count + 1

		




class Pagerunner:

	startAddress = ''	#	#	#	#	#The starting Address for the search
	module = None						#class which the pagerunner uses to perform actions on each page 
	moduleFilePath = None				#Path of the module that the webcrawler uses
	debugOn = False		#	#	#	#	#Enables/Disables debug text 
	verboseOn = False					#Enables/Disables verbose text (less detailed than debug text)
	domains = set()	#	#	#	#	#	#Domains that the runner is allowed to traverse
	tabooWords = set()					#Keywords that ban links from being searched by the runner
	responses = queue.Queue()	#	#	#responses that have yet to be processed
	processed = set()					#domains that the function thread has processed
	notVisited = queue.Queue()	#	#	#Adressses that the runner has not yet visited
	visited = set()						#Addresses tnat the runner has visited
	responseLock = threading.RLock()#	#Threading Lock for adding to the responses queue
	visitedLock = threading.RLock()		#Threading Lock for adding to the visited list
	notVisitedLock = threading.RLock()	#Threading Lock for adding to the queue
	saveFolder = 'saves/'				#Save directory for the crawler
	threads = set()	#	#	#	#	#	#List of the threads in use 
	timeOfLastSave = None				#Time of the last save function
	saveInterval = None	#	#	#	#	#Time elapsed since the last save operation
	startFromLoad = None				#whether or not the program is starting from as savefile
										#Next Line is the headers the runner uses when sending a request
	headers = {'Connection' : 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',}


	def __init__(self, newStartAddress=None, newDomains=None, newTabooWords=None, newDebugOn=False, newVerboseOn = False,  newThreadCount = 1, newModuleFilePath=None, newSaveInterval = None, newLoadPath=None ):
		if not Pagerunner.startAddress:
			Pagerunner.startAddress = newStartAddress
		
		Pagerunner.addLink(newStartAddress)

		if newSaveInterval:
			Pagerunner.saveInterval = newSaveInterval
			Pagerunner.timeOfLastSave = time.time()
		
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
		
		if newModuleFilePath:
			Pagerunner.moduleFilePath = newModuleFilePath
			Pagerunner.module = Pagerunner.handleImport(newModuleFilePath)
		else:
			Pagerunner.module = DoNothing()

		if Pagerunner.debugOn:	
			print('starting init process')

		if newLoadPath:
			Pagerunner.load(newLoadPath)
		else:
			Pagerunner.crawlPage(Pagerunner.nextLink())

		if Pagerunner.debugOn:
				print('''Data structure Status on init:
	visited: ''' + str(Pagerunner.visited) + ''' 
					
	domains: ''' + str(Pagerunner.domains) + '''
					
	notVisited: ''' + str(Pagerunner.notVisited.qsize()) + '''

	threads: ''' + str(Pagerunner.threads) )


		



		if Pagerunner.debugOn:	
			print('creating child threads')
		Pagerunner.createThreads(newThreadCount)
		

		if Pagerunner.debugOn:	
			print('starting child threads')
		Pagerunner.startThreads()
	
	@staticmethod
	def handleImport(fileName):
		i = importlib.import_module(fileName.replace('.py',''))
		return i.WebpageHandler()

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
		with Pagerunner.notVisitedLock:
			return Pagerunner.notVisited.empty()
	
	@staticmethod
	def responsesIsEmpty():
		with Pagerunner.responseLock:
			return Pagerunner.responses.empty()

	@staticmethod
	def addLink(newLink):
		with Pagerunner.notVisitedLock:
			Pagerunner.notVisited.put(newLink)

	@staticmethod
	def addLinks(newLinks):
		with Pagerunner.notVisitedLock:
			for  newLink in newLinks:
				Pagerunner.notVisited.put(newLink)
	
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
		with Pagerunner.notVisitedLock:
			nextLink =Pagerunner.notVisited.get(False)
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
					
	notVisited: ''' + str(Pagerunner.notVisited.qsize()) + '''

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
			print(str(e) + ' : ' +  pageUrl)
			returnlinks =  set()

		except UnicodeDecodeError as e:
			print(str(e) + ' : ' +  pageUrl)
			returnlinks =  set()

		except UnicodeEncodeError as e:
			print(str(e) + ' : ' +  pageUrl)			
			returnlinks =  set()

		except ConnectionResetError as e:
			print(str(e) + ' : ' +  pageUrl)
			returnlinks =  set()

		except ConnectionResetError as e:
			print(str(e) + ' : ' +  pageUrl)
			returnlinks =  set()

		except IncompleteRead as e:
			print(str(e) + ' : ' +  pageUrl)
			returnlinks =  set()

		finally:
			Pagerunner.visited.add(pageUrl)

		return returnlinks 

	@staticmethod
	def getOnlyResponse(url):
		response = None
		try:	
			request=Request(pageUrl,None,Pagerunner.headers) #The assembled request
			response = urlopen(request)

		except URLError as e:
			print(str(e) + ' : ' +  pageUrl)
			
		except UnicodeDecodeError as e:
			print(str(e) + ' : ' +  pageUrl)

		except UnicodeEncodeError as e:
			print(str(e) + ' : ' +  pageUrl)
			
		except ConnectionResetError as e:
			print(str(e) + ' : ' +  pageUrl)

		except ConnectionResetError as e:
			print(str(e) + ' : ' +  pageUrl)

		except IncompleteRead as e:
			print(str(e) + ' : ' +  pageUrl)

		finally:
			return response
	

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
			

			if Pagerunner.saveInterval and time.time() - Pagerunner.saveInterval  > Pagerunner.timeOfLastSave:
				print('saving progress')
				Pagerunner.saveProgress()
				Pagerunner.timeOfLastSave = time.time()
		
		Pagerunner.module.pipe( None,None,isLastRun=True)

	@staticmethod 
	def saveProgress():
		if Pagerunner.debugOn or Pagerunner.verboseOn:
			print('saving now')

		savePath = Pagerunner.saveFolder + Pagerunner.startAddress.replace('.', '[dot]').replace('http://','').replace('https://','') + '/'

		if not os.path.exists(savePath):
			os.makedirs(savePath)

		with Pagerunner.visitedLock, Pagerunner.notVisitedLock, Pagerunner.responseLock:

			with open(savePath+ time.ctime() + '.save', 'w') as file:
				
				file.write('[visited]\n')
				for elem in Pagerunner.visited:
					file.write(elem + '\n')

				file.write('[notVisited]\n')
				for elem in list(Pagerunner.notVisited.queue):
					file.write(str(elem) + '\n')

				file.write('[processed]\n')
				for elem in Pagerunner.processed:
					file.write(elem + '\n')

				file.write('[responses]\n')
				for elem in list(Pagerunner.responses.queue):
					file.write(str(elem[0]) + '\n')

				file.write('[domains]\n')
				for elem in Pagerunner.domains:
					file.write(elem + '\n')

				file.write('[tabooWords]\n')
				for elem in Pagerunner.tabooWords:
					file.write(elem + '\n')

				file.write('[startAddress]\n')
				file.write(Pagerunner.startAddress + '\n')
				file.write('[verboseOn]\n')
				file.write(str(Pagerunner.verboseOn) + '\n')
				file.write('[debugOn]\n')
				file.write(str(Pagerunner.debugOn) + '\n')
				file.write('[moduleFilePath]\n')
				file.write(str(Pagerunner.moduleFilePath) + '\n')
				
		if Pagerunner.debugOn or Pagerunner.verboseOn:
			print('save complete')


	@staticmethod
	def load(loadPath):
		currentTag = None
		with open(loadPath, 'r') as file:
			print('Loading from ' + loadPath)
			for line in file:
				if '[' in line and ']\n' in line:
					currentTag = line.replace('[', '').replace(']', '').replace('\n' , '')

				elif currentTag == 'visited':
					Pagerunner.visited.add(line.replace('\n' , ''))

				elif currentTag == 'notVisited':
					Pagerunner.notVisited.put(line.replace('\n' , ''))

				elif currentTag == 'processed':
					Pagerunner.processed.add(line.replace('\n' , ''))

				elif currentTag == 'responses':
					Pagerunner.responses.put((line.replace('\n', '') , Pagerunner.getOnlyResponse(line.replace('\n', ''))))

				elif currentTag == 'domains':
					Pagerunner.domains.add(line.replace('\n' , ''))

				elif currentTag == 'tabooWords':
					Pagerunner.tabooWords.add(line.replace('\n' , ''))

				elif currentTag == 'startAddress':
					Pagerunner.startAddress = line.replace('\n', '')

				elif currentTag == 'verboseOn':
					Pagerunner.verboseOn = bool(line.replace('\n', ''))

				elif currentTag == 'debugOn':
					Pagerunner.DebugOn = bool(line.replace('\n', ''))

				elif currentTag == 'moduleFilePath':
					Pagerunner.moduleFilePath = line.replace('\n', '')



