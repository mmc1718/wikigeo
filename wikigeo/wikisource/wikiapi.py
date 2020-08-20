import requests_html as r
from requests_html import HTML
import json
import math
from fuzzywuzzy import fuzz
import logging
import time


class WikipediaAPI(object):

    """sends queries to the Wikipedia API
    language options and stats can be found here: https://en.wikipedia.org/wiki/List_of_Wikipedias"""

    def __init__(self, userinfo, language='en'):
        self.headers = {"User-agent": userinfo}
        self.session = r.HTMLSession()
        self.url = "https://{}.wikipedia.org/w/api.php".format(language)
        self.data = None
        self.query = None

    def _send_query(self):
        """sends a query and saves response"""

        response = self.session.get(self.url, params=self.query, headers=self.headers)
        logging.debug(response)
        if(not response.ok):
            raise Exception(response)
        self.data = response.json()
        try:
            logging.warning(self.data['error'])
            raise Exception('Check parameters; ' + str(self.data))
        except KeyError:
            pass
    
    def _next_search_results(self):
        """gets next set of results for query response"""

        current_results = self.data
        while('continue' in current_results):
            logging.debug('getting next page')
            _continue = current_results['continue']
            self.query['continue'] = _continue
            self._send_query
            time.sleep(1)
            if(self.data == current_results):
                logging.debug('reached end of results')
                break
            for page, result in self.data['query']['pages'].items():
                try:
                    current_results['query']['pages'][page].update(result)
                except:
                    logging.warning(str(page) + 'missing from new results')
            self.data = current_results

    def search_nearby(self, lat, lon, limit, radiusmetres):
        """query to get wiki pages near a coordinate
        options for geosearch are found here: 
        https://en.wikipedia.org/w/api.php?action=help&modules=query+geosearch"""

        if(not isinstance(lat, float)):
            raise Exception('Check parameters; latitude must be a float')
        if(not isinstance(lon, float)):
            raise Exception('Check parameters; longitude must be a float')
        if((not isinstance(radiusmetres, int)) or (not 10 <= radiusmetres <= 10000)):
            raise Exception('Check parameters; radiusmetres must be an int between 10 and 10000')
        if((not isinstance(limit, int)) or (not 0 < limit <= 500)):
            raise Exception('Check parameters; limit must be an int between 1 and 500')

        self.query = {
        "format": "json",
        "generator": "geosearch",
        "ggscoord": "{}|{}".format(lat, lon),
        "ggslimit": "{}".format(limit),
        "ggsradius": "{}".format(radiusmetres),
        "action": "query",
        "prop": "coordinates|pageterms|pageimages"
        }
        
        self._send_query()
        self._next_search_results()
    
    def search_string(self, search_string, limit=5):
        """query to search wikipedia for pages containing search string.
        options for search found here: https://www.mediawiki.org/wiki/API:Search
        and for query here: https://www.mediawiki.org/wiki/API:Query"""
        
        if(not isinstance(search_string, str)):
            raise Exception('Check parameters; keyword must be a string')
        if((not isinstance(limit, int)) or (not 0 < limit <= 500)):
            raise Exception('Check parameters; limit must be an int between 1 and 500')

        self.query = {
            "format": "json",
            'generator': 'search',
            "gsrsearch": search_string.replace(' ', '+'),
            'gsrlimit': '{}'.format(limit),
            "action": "query",
            'prop': 'coordinates|pageterms|pageimages',
            'piprop': 'original|name',
            'coprop': 'type',
            'coprimary': 'all'
        }
        self._send_query()
        self._next_search_results()

    """
    def parse_page(self, pagetitle, to_parse=['text']):
        #query to parse a wiki page by page title.
        #options for what to parse can be found here:
         #https://www.mediawiki.org/wiki/API:Parsing_wikitext

        if(not isinstance(pagetitle, str)):
            raise Exception('Check parameters; pagetitle must be a string')
        if(not isinstance(to_parse, list)):
            raise Exception('Check parameters; to_parse must be a list of strings to parse')

        self.query = {
            "format": "json",
            "action": "parse",
            "page": '{}'.format(pagetitle),
            "prop": "{}".format('|'.join(to_parse)),
        }
        self._send_query()
    """

    def return_data(self):
        """output response data"""
        return self.data
    
class WikiCommonsAPI(WikipediaAPI):

    """sends queries to the wiki commons api"""

    def __init__(self, userinfo):
        super().__init__(userinfo)
        self.url = "https://commons.wikimedia.org/w/api.php"
    
    def search_nearby(self, lat, lon, radiusmetres):
        """get images near given coordinates from wikimedia commons.
        options for image info are found here:
         https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bimageinfo"""

        if(not isinstance(lat, float)):
            raise Exception('Check parameters; latitude must be a float')
        if(not isinstance(lon, float)):
            raise Exception('Check parameters; longitude must be a float')
        if((not isinstance(radiusmetres, int)) or (not 10 <= radiusmetres <= 10000)):
            raise Exception('Check parameters; radiusmetres must be an int between 10 and 10000')

        self.query = {
            'format': 'json',
            'action': 'query',
            'generator': 'geosearch',
            'ggscoord': "{}|{}".format(lat, lon),
            'ggslimit': 5,
            'prop': 'imageinfo|imagelabels',
            'iilimit': 1,
            'iiprop': 'url',
            'iiurlwidth': '250',
            'iiurlheight': '250',
            'ggsradius': "{}".format(radiusmetres),
            'ggsnamespace': '6',
            'ggsprimary': 'all'
        }
        self._send_query()
        self._next_search_results()


if __name__ == '__main__':

    
    from pprint import pprint

    commons = WikiCommonsAPI("test test@example.com")
    wiki = WikipediaAPI("test test@example.com")

    def run_search_nearby():
        wiki.search_nearby(51.43295, -0.5114918947219849, 10, 10000)
        return wiki.return_data()
    
    def run_parse_page():
        wiki.parse_page("Antrim Coast and Glens", to_parse=['text', 'sections'])
        return wiki.return_data()
    
    def run_search_string():
        wiki.search_string('Staines Bridge', limit=5)
        return wiki.return_data()

    def run_commons_search_nearby():
        commons.search_nearby(45.78024, -34.91654, 1000)
        return commons.return_data()
    
    start = time.time()
    pprint(run_commons_search_nearby())
    end = time.time()
    print('time taken:', end-start)
