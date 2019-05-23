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
	-v: verbose output, prints more to the screen while it works
	
	-m <filename>: module to use, cli implementation requires a class named webpagehandler and the function pipe(self,url,response,isLastRun)
	
	-d <domain 1> ... : adds listed domains to the set of authorized domains
	
	-t <taboo 1> ... : adds listed taboos to the set of keywords websites may not have in order to be visited
	
	-s <interval> : saves every <interval> seconds

	--debug: debug mode, prints the status of all of the data structures in use for the duration of the run in each iteration
	
	--threads [int]: manually specify the number of threads to use
	'''

def checkFormat(url):
	if ('http://' not in url[0:7]) and ('https://' not in url[0:8]):
		url = 'https://' + url 

	return url

def parseToSet(startingIndex, numberOfArguments):
	i = startingIndex + 1
	newset = set()
	while i < numberOfArguments:
		if '-' in sys.argv[i]:
			break
		
		newset.add(sys.argv[i])
		i+=1 

	return newset

def parse():
	arguments = dict()

	if len(sys.argv) < 2:
		print(usage())
		exit(0)

	arguments['website'] = checkFormat(sys.argv[1]).lower()
	arguments['debug'] = False
	arguments['verbose'] = False
	arguments['threads'] = os.cpu_count() * 10
	arguments['modulePath'] = None
	arguments['taboos'] = set()
	arguments['focus'] = set()
	arguments['domains'] = set()
	arguments['saveInterval'] = None
	arguments['loadPath'] = None

	if len(sys.argv )>2 :	
		for i in range(len(sys.argv)):
			if sys.argv[i].lower() == '--debug':
				arguments['debug'] = True
			elif sys.argv[i].lower() == '--threads':
				arguments['threads'] = int(sys.argv[i+1])
			elif sys.argv[i].lower() == '-v':
				arguments['verbose'] = True
			elif sys.argv[i].lower() == '-m':
				arguments['modulePath']= sys.argv[i+1]
			elif sys.argv[i].lower() == '-t': 
				arguments['taboos'] = parseToSet(i, len(sys.argv))
			elif sys.argv[i].lower() == '-f': 
				arguments['focus'] = parseToSet(i, len(sys.argv))
			elif sys.argv[i].lower() == '-d': 
				arguments['domains'] = parseToSet(i, len(sys.argv))
			elif sys.argv[i].lower() == '-h' or sys.argv[i].lower() == '--help':
				print(usage())
				exit(0) 
			elif sys.argv[i].lower() == '-s':
				if i + 1 < len(sys.argv) and '-' not in sys.argv[i+1]:
					arguments['saveInterval'] = int(sys.argv[i+1]) 
				else:
					arguments['saveInterval'] = 60
			elif sys.argv[i].lower() == '-l':
				arguments['loadPath'] = sys.argv[i+1] 
				

	return arguments


def main():	
	arguments = parse()
	arguments['domains'].add(get_domain_name(arguments['website']))
	if arguments['debug']: 
		print('website : '  + arguments['website'])
		print('taboos: ' + str(arguments['taboos']))


	Pagerunner(newStartAddress=arguments['website'], newDomains=arguments['domains'], newTabooWords=arguments['taboos'], newDebugOn=arguments['debug'], newVerboseOn=arguments['verbose'], newThreadCount=arguments['threads'],newModuleFilePath=arguments['modulePath'], newSaveInterval=arguments['saveInterval'], newLoadPath=arguments['loadPath'], newFocusWords=arguments['focus'])
	#Pagerunner.startThreads()
	
	






if __name__ == '__main__':
	main()
else:
	print('no main')