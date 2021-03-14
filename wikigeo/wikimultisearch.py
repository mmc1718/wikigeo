from wikigeo.wikisearch import WikiExtractor
from wikigeo.wikisource.wikitext import WikiText
import concurrent.futures
import time
import logging

class ConcurrentSearcher(object):

    """
    
    Runs search methods with multiple sets of parameters concurrently.  
    Keep max searches low so as not to request more than 50 pages in a minute (conservative estimate)
    
    """

    def __init__(self, language, userinfo, maxlimit=True):
        """

        for language code options: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        for info on user details see: https://www.mediawiki.org/wiki/API:Etiquette#The_User-Agent_header

        """
        self.wiki = WikiExtractor(language, userinfo)
        self.maxlimit = maxlimit
        self.language = language
    
    def multi_nearby_pages(self, coordpairs, limit=4, radiusmetres=10000):
        """
        
        gets nearby pages from multiple sets of coordinates.

        coordpairs: a list of tuples containing lat lon pairs

        limit: int, max number of pages to return

        returns a list of results. Each result is a dictionary with a 'result' key containing a list of dictionaries (one page per dictionary), with 'title', 'label', 'description', 'coordinates', 'image'.
        Results are outputted in the same order of the given coords.

        [{'coords': (lat, lon), 'result': [{result1}, {result2} ...]}, ...]
        
        """

        if(self.maxlimit):
            if(len(coordpairs) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")

        lats = [coordpair[0] for coordpair in coordpairs]
        lons = [coordpair[1] for coordpair in coordpairs]
        limit = [limit for coordpair in coordpairs]
        radiusmetres = [radiusmetres for coordpair in coordpairs]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.wiki.get_nearby_pages, lats, lons, limit, radiusmetres)
        output = [{'coords': coordpair, 'result': result} for coordpair, result in zip(coordpairs, results)]
        return output
        

    def multi_page_text(self, titles, textlen):
        """
        
        Gets text from multiple pages by title.

        titles: list of wiki page titles

        textlen: optional, int representing character limit for text returned.

        returns a list of dictionaries of headers and text for each page

        [{'title': inputtedtitle, 'text': textresult}, ...]
        
        """

        if(self.maxlimit):
            if(len(titles) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")
        
        if(not isinstance(textlen, int)):
            raise Exception('invalid textlen argument; must be one of False or an integer')
        scraper = WikiText(textlen, self.language)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(scraper.scrape_page_text, titles)
        output = [result for result in results]
        return output

    def multi_nearby_images(self, coordpairs, namestomatch=False, radiusmetres=10000, matchfilter=False):
        """
        
        Gets images nearby for each coord pair.

        coordpairs: a list of tuples containing lat lon pairs

        namestomatch: a list of names to match with each lat lon pair

        radiusmetres: an int max 10000, distance from coords to search (default 10000)

        matchfilter: either False or an int representing min name match value for results with a name to match (between 0 and 100)
        
        returns list of dictionary of results
        [{'coords: latlon, 'result': [result1, result 2, ...]}, ...]

        Notes: inputs of coords and names must in the same order to match and must be same length
        (if names are missing use False as placeholder)
        
        """
        
        if(self.maxlimit):
            if(len(coordpairs) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")

        lats = [coordpair[0] for coordpair in coordpairs]
        lons = [coordpair[1] for coordpair in coordpairs]
        if(not namestomatch):
            namestomatch = [False for coordpair in coordpairs]
        radiusmetres = [radiusmetres for coordpair in coordpairs]
        matchfilters = []
        for name in namestomatch:
            if(name):
                matchfilters.append(matchfilter)
            else:
                matchfilters.append(False)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.wiki.get_nearby_images, lats, lons, radiusmetres, namestomatch, matchfilters)
        output = [{'coords': coordpair, 'result': result} for coordpair, result in zip(coordpairs, results)]
        return output

    def multi_page_match(self, searches, bestmatch=False, maxdistance=30, minnamematch=0):
        """
        
        Gets suggested page match for each keyword and coordpair in searchparams.

        searches: a list of tuples containing keyword (string), lat (float), lon (float)

        bestmatch: 

        bestmatch='name' will return the best (highest on scale 0-100) match based 
        on keyword matching page title 

        bestmatch='distance' will return the best (closest) match on distance

        bestmatch=False will return all geolocated matches nearby

        maxdistance: int, results must be less than the max distance in km of results from search coords (default 30)
        
        minnamematch: int, results must have a higher name match than minnamematch, between 0-100 (default 50)
        
        returns a list of dictionary/lists of dictionaries containing page title, 
        description, label, image, distance, coords and match rating
        
        [{'keyword': input, 'result': [{result1}, {result2}, ...]}, ...]

        """

        if(self.maxlimit):
            if(len(searches) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")
        
        keywords = [search[0] for search in searches]
        lats = [search[1] for search in searches]
        lons = [search[2] for search in searches]
        bestmatch = [bestmatch for search in searches]
        maxdistance = [maxdistance for search in searches]
        minnamematch = [minnamematch for search in searches]
        logging.debug(keywords)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.wiki.get_page_match, keywords, lats, lons, bestmatch, maxdistance, minnamematch)
            print(list(results))
        output = [{'keyword': keyword, 'result': result} for keyword, result in zip(keywords, results)]
        return output
