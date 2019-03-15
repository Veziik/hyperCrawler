#!/usr/bin/env python3
# coding: utf-8
from urllib.request import urlopen
from urllib.request import Request
import sys
import os
from queue import Queue
from domain import *
from pagerunner import Pagerunner


def usage():
	return '''usage:
	./main <website>'''

def checkFormat(url):
	if ('http://' not in url[0:7]) and ('https://' not in url[0:8]):
		url = 'https://' + url 

	return url

def parse():
	arguments = dict()

	if len(sys.argv) < 2:
		print(usage())
		exit(0)

	arguments['website'] = checkFormat(sys.argv[1])
	arguments['debug'] = False
	arguments['verbose'] = False
	arguments['threads'] = os.cpu_count()

	if len(sys.argv )>2 :	
		for i in range(len(sys.argv)):
			if sys.argv[i] == '-d':
				arguments['debug'] = True
			elif sys.argv[i] == '-t':
				arguments['threads'] = int(sys.argv[i+1])
			elif sys.argv[i] == '-v':
				arguments['verbose'] = True

	return arguments


def main():	
	arguments = parse()
	if arguments['debug']: 
		print('website : '  + arguments['website'])
	Pagerunner(newStartAddress=arguments['website'], newDomains={get_domain_name(arguments['website'])}, newTabooWords=None, newDebugOn=arguments['debug'], newVerboseOn=arguments['verbose'], newThreadCount=arguments['threads'] )
	#Pagerunner.startThreads()
	
	






if __name__ == '__main__':
	main()
else:
	print('no main')