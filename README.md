#hypercrawler

Built from the framework prvided by thenewbostion, but improves on speed through faster data structures.

domainscraper.py and link_finder.py are all code from thenewboston

usage: main.py [URL]

Options
-v: verbose output, prints more to the screen while it works
-f [filename]: function to use, the hypercrawler will import the given file and use the function called 'target'. Note that the function needs to at least handle the URL and Response, in that order.
-d [domain 1] ... : adds listed domains to the set of authorized domains
-t [taboo 1] ... : adds listed taboos to the set of keywords websites may not have in order to be visited
--Debug: debug mode, prints the status of all of the data structures in use for the duration of the run in each iteration
--Threads [int]: manually specify the number of threads to use