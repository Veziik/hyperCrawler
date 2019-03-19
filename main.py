#!/usr/bin/env python3
# coding: utf-8
from urllib.request import urlopen
from urllib.request import Request
import sys
import os
from queue import Queue
from domain import *
from pagerunner import Pagerunner
import importlib


def usage():
	return '''

usage: ''' + sys.argv[0] +''' <URL>

Options
	-v: 					verbose output, prints more to the screen while it works
	-f <filename>: 			function to use, requires a class named webpagehandler and the function pipe(url,response)
	-d <domain 1> ... : 	adds listed domains to the set of authorized domains
	-t <taboo 1> ... : 		adds listed taboos to the set of keywords websites may not have in order to be visited
	--debug: 				debug mode, prints the status of all of the data structures in use for the duration of the run in each iteration
	--threads [int]: 		manually specify the number of threads to use
	'''

def checkFormat(url):
	if ('http://' not in url[0:7]) and ('https://' not in url[0:8]):
		url = 'https://' + url 

	return url

def handleImport(fileName):
	i = importlib.import_module(fileName.replace('.py',''))
	return (i.WebpageHandler.pipe,i.WebpageHandler())

def printPageNames(pageUrl, response):
	print(str(len(Pagerunner.visited)) + ': ' + pageUrl)

def parseToSet(startingIndex, numberOfArguments):
	i = startingIndex + 1
	taboos = set()
	while i < numberOfArguments:
		if '-' in sys.argv[i]:
			break
		
		taboos.add(sys.argv[i])
		i+=1 

	return taboos

def parse():
	arguments = dict()

	if len(sys.argv) < 2:
		print(usage())
		exit(0)

	arguments['website'] = checkFormat(sys.argv[1])
	arguments['debug'] = False
	arguments['verbose'] = False
	arguments['threads'] = os.cpu_count()
	arguments['function'] = printPageNames
	arguments['taboos'] = set()
	arguments['domains'] = set()
	arguments['handler'] = None

	if len(sys.argv )>2 :	
		for i in range(len(sys.argv)):
			if sys.argv[i].lower() == '--debug':
				arguments['debug'] = True
			elif sys.argv[i].lower() == '--threads':
				arguments['threads'] = int(sys.argv[i+1])
			elif sys.argv[i].lower() == '-v':
				arguments['verbose'] = True
			elif sys.argv[i].lower() == '-f':
				(arguments['function'],arguments['handler'])= handleImport(sys.argv[i+1])
			elif sys.argv[i].lower() == '-t': 
				arguments['taboos'] = parseToSet(i, len(sys.argv))
			elif sys.argv[i].lower() == '-d': 
				arguments['domains'] = parseToSet(i, len(sys.argv))
			elif sys.argv[i].lower() == '-h' or sys.argv[i].lower() == '--help':
				print(usage())
				exit(0) 

	return arguments


def main():	
	arguments = parse()
	arguments['domains'].add(get_domain_name(arguments['website']))
	if arguments['debug']: 
		print('website : '  + arguments['website'])
		print('taboos: ' + str(arguments['taboos']))


	Pagerunner(newStartAddress=arguments['website'], newDomains=arguments['domains'], newTabooWords=arguments['taboos'], newDebugOn=arguments['debug'], newVerboseOn=arguments['verbose'], newThreadCount=arguments['threads'],newFunction=arguments['function'])
	#Pagerunner.startThreads()
	
	






if __name__ == '__main__':
	main()
else:
	print('no main')