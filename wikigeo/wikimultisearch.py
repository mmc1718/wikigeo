from wikigeo.wikisearch import WikiExtractor
from wikigeo.wikisource.wikiscrape import WikiScraper
import concurrent.futures
import time
import logging

class ConcurrentSearcher(object):

    """runs search methods with multiple sets of parameters concurrently
    keep max searches low so as not to request more than 50 pages in a minute (conservative)"""

    def __init__(self, language, userinfo, maxlimit=True):
        self.wiki = WikiExtractor(language, userinfo)
        self.maxlimit = maxlimit
        self.language = language
    
    def multi_nearby_pages(self, coordpairs, toget=['titles'], limit=4, radiusmetres=10000):
        """gets nearby pages from multiple sets of coordinates.

        coordpairs: a list of tuples containing lat lon pairs
        toget: list containing any of 'titles', 'labels', 'descriptions', 'coordinates', 'images'

        returns a list of dictionaries of arrays containing requested info in the order of the coords
        {'coords': inputted coords, 'result': requestedinfo}"""

        if(self.maxlimit):
            if(len(coordpairs) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")

        lats = [coordpair[0] for coordpair in coordpairs]
        lons = [coordpair[1] for coordpair in coordpairs]
        toget = [toget for coordpair in coordpairs]
        limit = [limit for coordpair in coordpairs]
        radiusmetres = [radiusmetres for coordpair in coordpairs]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.wiki.get_nearby_pages, lats, lons, toget, limit, radiusmetres)
        output = [{'coords': coordpair, 'result': result} for coordpair, result in zip(coordpairs, results)]
        return output
        

    def multi_page_text(self, titles, textlen, translateto):
        """gets text from multiple pages

        titles: list of wiki page titles
        textlen: int representing character limit for text returned
        returns a list of dictionaries of headers and text for each page
        {'title': inputtedtitle, 'result': dictionaryresult}"""

        if(self.maxlimit):
            if(len(titles) > 50):
                raise Exception("""Making more than 50 parallel requests is not advised. 
            See https://www.mediawiki.org/wiki/API:Etiquette#Request_limit for details
            and https://phabricator.wikimedia.org/ for advice on api limits. 
            To bypass add maxlimit=False as a parameter for ConcurrentSearcher""")
        
        textlen = [textlen for title in titles]
        scraper = WikiScraper(self.language)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(scraper.scrape_page_text, titles, textlen)
        if(translateto):
            data = [result for result in results]
            translated = scraper.translate_text([record['text'] for record in data], translateto)
            output = [{'title': record['title'], 'text': translation} for record, translation in zip(data, translated)]
        else:
            output = [result for result in results]
        return output

    def multi_nearby_images(self, coordpairs, namestomatch=False, radiusmetres=10000, matchfilter=False):
        """gets images nearby for each coord pair

        coordpairs: a list of tuples containing lat lon pairs
        namestomatch: a list of names to match with each lat lon pair
        matchfilter: an int representing min name match value for results with a name to match (between 0 and 100)
        
        Notes: inputs of coords and names must in the same order to match and must be same length
        (if names are missing use False as placeholder)"""
        
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

    def multi_page_match(self, searches, bestmatch=False, maxdistance=30, minnamematch=50):
        """gets suggested page match for each keyword and coordpair in searchparams

        searches: a list of tuples containing keyword, lat, lon
        returns a list of dictionary/lists of dictionaries containing page title, description, label, image, distance, coords
        and match rating"""

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
        output = [{'keyword': keyword, 'result': result} for keyword, result in zip(keywords, results)]
        return output

if __name__ == '__main__':

    searcher = ConcurrentSearcher('en', "test")

    coords = [
        (51.19482552438797, -0.4718933366807213),
        (51.374798908124774, -0.7340422319483855),
        (51.4368078571564, -0.6332591317376522),
        (51.655000856037724, 0.0462537139415177),
        (51.18393717250045, -0.825727955629195),
        (51.39861787462966, -1.6807673580284554),
        (51.28843277725252, 0.2476129201376236),
        (51.060624488352296, -0.1604187830896187),
        (51.18583407040071, -0.4277369182879632),
        (51.17760083671381, -0.4678810897599431),
        (51.31329596922965, -0.8473433886048575),
        (50.86854995219705, -0.595084718328369),
        (51.20350736842405, -0.5098952878865604),
        (51.19602085336275, -0.3437139175401044),
        (51.576395258503034, -0.8885315837655247),
        (51.264756998405, -0.0802098823552504),
        (51.23663654353719, -0.4967295882528549),
        (51.44703831439468, -1.259597850115957),
        (51.76944281382442, -1.3282675046155552),
        (51.01711299594329, -1.429038088916859),
        (51.326791473315296, -0.3057011313377656),
    ]

    def run_nearby_pages():
        #coords = [(55.94631, -3.16552), (51.43399588542416, -0.5114918947219849)]
        print(searcher.multi_nearby_pages(coords, toget=['images'], limit=5, radiusmetres=8000))
    
    def run_page_text():
        titles = ['Staines-upon-Thames', 'Edinburgh', 'Killeter', 'Northern Ireland', 'Staines Moor', 
        'Epping Forest', 'France', 'Greater_London', 'Paris', 'Scotland', 'England', 'Manchester', 'Hyde Park', 
        'Birmingham', 'Surrey', 'Kent', 'South_East_England', 'Berkshire', 'City of London', 'Central_London']

        titles2 = ['Staines-upon-Thames', 'Edinburgh']
        result = searcher.multi_page_text(titles, textlen=50, translateto=False)
        print(result)
    
    def run_nearby_images():
        coords = [(55.94631, -3.16552), (51.43399588542416, -0.5114918947219849)]
        names = ["Edinburgh", False]
        print(searcher.multi_nearby_images(coords, names, matchfilter=40))

    def run_page_match():
        searches = [("Arthur's Seat", 55.94631, -3.16552), ('Staines', 51.43399588542416, -0.5114918947219849)]
        print(searcher.multi_page_match(searches, bestmatch=True, minnamematch=0))

    start = time.time()
    run_page_text()
    end = time.time()
    print('time taken:', end-start)
