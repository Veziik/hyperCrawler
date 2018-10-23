#!/usr/bin/env python3
# coding: utf-8
from urllib.request import urlopen
from urllib.request import Request
import sys
from queue import Queue
from domain import *
from pagerunner import Pagerunner


def usage():
	return '''usage:
	./main <website>'''

def parse():
	arguments = dict()

	if len(sys.argv) < 2:
		print(usage())
		exit(0)

	arguments['website'] = sys.argv[1]
	arguments['debug'] = False
	arguments['threads'] = 1

	if len(sys.argv )>2 :	
		for i in range(len(sys.argv)):
			if sys.argv[i] == '-d':
				arguments['debug'] = True
			elif sys.argv[i] == '-t':
				arguments['threads'] = int(sys.argv[i+1])

	return arguments


def main():
	arguments = parse()
	Pagerunner(newStartAddress=arguments['website'], newDomains=get_domain_name(arguments['website']), newTabooWords=None, newDebugOn=arguments['debug'], newThreadCount=arguments['threads'] )
	Pagerunner.start()
	
	






if __name__ == '__main__':
	main()
else:
	print('no main')