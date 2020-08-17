import requests_html as r
from requests_html import HTML
import json
from pprint import pprint
import math
from fuzzywuzzy import fuzz
import logging

# look into async

class Wikipedia(object):

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
        self.data = response.json()
    
    def _next_search_results(self):
        """gets next set of results for query response"""
        current_results = self.data
        while('continue' in current_results):
            print('getting next page')
            _continue = current_results['continue']
            self.query['continue'] = _continue
            self._send_query
            if(self.data == current_results):
                print('reached end of results')
                break
            #pprint(new_results)
            for page, result in self.data['query']['pages'].items():
                try:
                    current_results['query']['pages'][page].update(result)
                except:
                    logging.warning(str(page) + 'missing from new results')
            self.data = current_results

    def search_nearby(self, lat, lon, limit, radiusmetres):
        """query to get wiki pages near a coordinate"""
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
        """query to search wikipedia for pages containing search string."""
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

    def parse_page(self, pagetitles=[], to_parse=['text']):
        """query to parse a wiki page by page title.
        options for what to parse can be found at https://www.mediawiki.org/wiki/API:Parsing_wikitext"""
        self.query = {
            "format": "json",
            "action": "parse",
            "page": '|'.join(pagetitles),
            "prop": "{}".format('|'.join(to_parse)),
        }
        self._send_query()

    def return_data(self):
        """output response data"""
        return self.data
    
class WikiCommons(Wikipedia):

    """sends queries to the wiki commons api"""

    def __init__(self, userinfo):
        super().__init__(userinfo)
        self.url = "https://commons.wikimedia.org/w/api.php"
    
    def search_nearby(self, lat, lon, radiusmetres=10000):
        """get images near given coordinates from wikimedia commons.
        options for image info are found here https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bimageinfo"""
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

    commons = WikiCommons("DaytripApp (marymcguire1718@gmail.com)")
    wiki = Wikipedia("DaytripApp (marymcguire1718@gmail.com)")

    def run_search_nearby():
        wiki.search_nearby(51.43295, -0.5118, 20, 1000)
        pprint(wiki.return_data())
    
    def run_parse_page():
        wiki.parse_page(["Antrim Coast and Glens"], to_parse=['text', 'sections'])
        print(wiki.return_data())
    
    def run_search_string():
        wiki.search_string('Staines Bridge', limit=5)
        pprint(wiki.return_data())

    def run_commons_search_nearby():
        commons.search_nearby(51.43295, -0.5118)
        print(commons.return_data())
    
    run_commons_search_nearby()
