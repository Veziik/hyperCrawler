#!/usr/bin/env python3
# coding: utf-8
from urllib.request import urlopen
from urllib.request import Request
import threading
import sys
from queue import Queue
from spider import Spider
from domain import *
from general import *
from sqlwriter  import *

HOMEPAGE = sys.argv[1]
DOMAIN_NAME = get_domain_name(HOMEPAGE)
PROJECT_NAME = (DOMAIN_NAME.split('.'))[0]
FILE_DIRECTORY = 'scripts'
QUEUE_FILE = FILE_DIRECTORY + '/queue.txt'
CRAWLED_FILE = FILE_DIRECTORY + '/crawled.txt'
CRAWLED_FILE = FILE_DIRECTORY + '/databased.txt'
SQL_FILE = FILE_DIRECTORY + '/' + PROJECT_NAME + '.sql'
NUMBER_OF_THREADS = 8
queue = Queue()
crawled = set()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME, FILE_DIRECTORY)


def create_workers():
	for _ in range(NUMBER_OF_THREADS):
		t = threading.Thread(target=work)
		t.daemon = True
		t.start()


def work():
	while True:
		url = queue.get();
		Spider.crawl_page(threading.current_thread().name, url)
		queue.task_done()

def create_jobs():
	for link in file_to_set(QUEUE_FILE):
		queue.put(link)
	queue.join()
	crawl()


def crawl():
	queued_links = file_to_set(QUEUE_FILE)
	if len(queued_links) > 0 :
		print(str(len(queued_links)) + " Links left in queue")
		create_jobs()


while True:
	try:
		
		create_workers()
		crawl()
	
	except KeyboardInterrupt:
		print('\nKeyboard Interrupt recieved, exiting')
		sys.exit(0)