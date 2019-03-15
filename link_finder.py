from html.parser import HTMLParser
from urllib import parse 

### All of this code was given to me by thenewboston 
### as a part of his videoseries on how to make a web crawler
class LinkFinder(HTMLParser):

	def __init__(self, base_url, page_url):
		super().__init__()
		self.base_url = base_url
		self.page_url = page_url
		self.links = set()

	def handle_starttag(self,tag,attrs):
		if tag == 'a':
			for (attrubite,value) in attrs:
				if attrubite == 'href':
					url = parse.urljoin(self.base_url,value)
					self.links.add(url)
		if tag == 'img':
			for (attrubite,value) in attrs:
				if attrubite == 'src':
					url = parse.urljoin(self.base_url,value)
					self.links.add(url)
		if tag == 'script':
			for (attrubite,value) in attrs:
				if attrubite == 'src':
					url = parse.urljoin(self.base_url,value)
					self.links.add(url)
		if tag == 'video':
			for (attrubite,value) in attrs:
				if attrubite == 'src':
					url = parse.urljoin(self.base_url,value)
					self.links.add(url)
		if tag == 'source':
			for (attrubite,value) in attrs:
				if attrubite == 'src':
					url = parse.urljoin(self.base_url,value)
					self.links.add(url)


	def page_links(self):
		return self.links

	def error(self, message):
		pass



