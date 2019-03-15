#hypercrawler

Built from the framework prvided by thenewbostion, but improves on speed through faster data structures.

usage: main.py [URL]

domainscraper.py and link_finder.py are all code from thenewboston

Options
-v: verbose output, prints more to the screen while it works
-d: debug mode, prints the status of all of the data structures in use for the duration of the run in each iteration
-f [filename]: function to use, the hypercrawler will import the given file and use the function called 'target'. Note that the function needs to at least handle the URL and Response, in that order.
