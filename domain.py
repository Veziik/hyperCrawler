from urllib.parse import urlparse
### All of this code was given to me by thenewboston 
### as a part of his videoseries on how to make a web crawler

def get_domain_name(url):
	try:
		results = get_sub_domain_name(url).split('.')
		return results[-2] + '.' + results[-1]
	except:
		return ''

def get_sub_domain_name(url):
	try:
		return urlparse(url).netloc
	except:
		return ''