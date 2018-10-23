#!/usr/bin/env python3
# coding: utf-8
from urllib.request import urlopen
from urllib.request import Request
import threading
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

	if len(sys.argv )>2 :	
		for arg in sys.argv:
			if arg == '-d':
				arguments['debug'] = True

	return arguments


def main():
	arguments = parse()
	Pagerunner(newStartAddress=arguments['website'], newDomains=get_domain_name(arguments['website']), newTabooWords=None, newDebugOn=arguments['debug'] )
	threadList = []
	i = 0
	
	while i < 4:
		name = 'thread ' + str(i)
		t = threading.Thread(target = Pagerunner.work(name))
		threadList.append(t)
		t.daemon = True

		if arguments['debug']:
			print(name + ' created')
		i+=1

		t.start()
	
	






if __name__ == '__main__':
	main()
else:
	print('no main')