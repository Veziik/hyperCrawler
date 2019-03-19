#! /usr/bin/env python3
from pagerunner import *
from domain import *

class WebpageHandler(object):
	
	pagetypes = dict()

	def __init__(self):
		pass
	
	def pipe(self, pageUrl,response, isLastRun):

		if not isLastRun:
			print('Pages Scanned: ' + str(len(Pagerunner.visited)) + 'ish ' + pageUrl)
			contentType = str(response.headers.get('content-type'))

			if contentType not in WebpageHandler.pagetypes:
				WebpageHandler.pagetypes[contentType] = set()
		
			WebpageHandler.pagetypes[contentType].add(pageUrl)


		else:
			filename='reports/'+ 'test.txt'

			with open(filename, 'w') as file:
				for ( key, value ) in WebpageHandler.pagetypes.items():
					file.write('Content Type: ' + key + '\n')
					file.write('Number of this Type: ' + str(len(value)) + '\n')
				
					for name in value:
						file.write('\t' + name + '\n\n')

					file.write('\n\n')



