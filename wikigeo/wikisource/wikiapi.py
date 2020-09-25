import requests_html as r
from requests_html import HTML
import json
import math
import re
import logging
import time



class WikipediaAPI(object):

    """sends queries to the Wikipedia API
    language options and stats can be found here: https://en.wikipedia.org/wiki/List_of_Wikipedias"""

    def __init__(self, userinfo, language='en'):
        self.headers = {"User-agent": userinfo}
        self.session = r.HTMLSession()
        self.url = "https://{}.wikipedia.org/w/api.php".format(language)
        self.result = {}
        self.data = {}
        self.query = None

    def _send_query(self):
        """sends a query and saves response"""

        logging.debug('query: ' + str(self.query))
        response = self.session.get(self.url, params=self.query, headers=self.headers)
        logging.debug(response)
        if(not response.ok):
            raise Exception(response)
        self.result = response.json()
        try:
            logging.warning(self.result['error'])
            raise Exception('Check parameters; ' + str(self.data))
        except KeyError:
            pass
    
    def _next_search_results(self):
        """gets next set of results for query response"""

        # saving result to data
        self.data = self.result.copy()
        while('continue' in self.result):
            # copying result
            page = self.result.copy()
            logging.debug('getting next page')
            logging.debug(self.result['continue'])
            # adding continue parameters to query
            for contparam, value in self.result['continue'].items():
                self.query[contparam] = value
            #_continue = current_results['continue']
            #self.query['continue'] = _continue
            self._send_query()
            time.sleep(1)
            logging.debug('previous page: ' + str(page))
            logging.debug('new page: ' + str(self.result))
            # checking if new results are the same as the previous
            if(self.result == page):
                logging.debug('reached end of results')
                break
            # updating data
            for article, result in self.result['query']['pages'].items():
                try:
                    # updating the old results
                    self.data['query']['pages'][article].update(result)
                except:
                    logging.debug(str(page) + 'missing from new results')
            if 'batchcomplete' in self.result:
                logging.debug('reached end of batch')
                break
            # setting the data to equal the newly updated results
            # self.data = current_results

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
            'gsrlimit': f'{limit}',
            'colimit': f'{limit}',
            "action": "query",
            'prop': 'coordinates|pageterms|pageimages',
            'piprop': 'original|name',
            'coprop': 'type',
            'coprimary': 'primary'
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
            'prop': 'imageinfo|imagelabels|coordinates',
            'iilimit': 1,
            'iiprop': 'url|extmetadata',
            'iiurlwidth': '250',
            'iiurlheight': '250',
            'ggsradius': "{}".format(radiusmetres),
            'ggsnamespace': '6',
        }
        self._send_query()
        self._next_search_results()

if __name__ == '__main__':

    from pprint import pprint

    coords = [51.477106480966924, -0.05733484162192326]

    wiki = WikiCommonsAPI('')
    wiki.search_nearby(coords[0], coords[1], 10000)
    pprint(wiki.return_data())
