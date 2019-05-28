#hypercrawler

Built from the framework prvided by thenewbostion, but improves on speed with faster data structures.
	
#Command Line
	usage: ./cli.py <URL>

Options

	-v: verbose output, prints more to the screen while it works
	-m <filename>: module to use, cli implementation requires a class named webpagehandler and the function pipe(self,url,response,isLastRun)	
	-d <domain 1> ... : adds listed domains to the set of authorized domains
	-t <taboo 1> ... : adds listed taboos to the set of keywords websites may not have in order to be visited
	-s <interval> : saves every <interval> seconds
	--debug: debug mode, prints the status of all of the data structures in use for the duration of the run in each iteration
	--threads [int]: manually specify the number of threads to use

#import documentation

First import:

	import Pagerunner

then set arguments:

	Pagerunner( arg1, ... , arg n)

the crawler will immediately start the scan with given arguments, arguments are as follows:
	
	newStartAddress=None	(string): Starting address of the crawler
	newModuleFilePath=None	(string): File path of module containing user's custom function
	newLoadPath=None		(string): File path of savefile to load from, overrides all other options 
	newDomains=None			(set) 	: Domains within which the crawler must remain, 'None' gives no restrictions
	newTabooWords=None		(set)	: Words which any prospective URL must not contain in order to be scanned
	newFocusWords=None		(set)	: Words which any prospective URL must contain in order to be scanned
	newDebugOn=False		(bool)	: Toggles the printing of the module's debug text
	newVerboseOn = False	(bool)	: Toggles the printing of the module's vebose output, less detailed than the debug flag
	newThreadCount = 1		(int)	: Specifies the number of threads to use, recommended is coresx10 
	newSaveInterval = None	(int)	: Specifies time, in seconds, between save operations


#more on importing custom functions

if given the path to a module, the crawler will attempt to import the module "WebpageHelper" and execute the function "pipe(self, pageUrl,response, isLastRun)"