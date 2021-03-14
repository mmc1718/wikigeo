import configparser
import unittest
from pprint import pprint
from wikigeo.wikisource.wikiapi import WikipediaAPI, WikiCommonsAPI

config = configparser.ConfigParser()
config.read('config.ini')

USER_DETAILS = f"{config['USER']['app']} {config['USER']['email']}"
QUERY = {
        "format": "json",
        "generator": "geosearch",
        "ggscoord": "51.43295|-0.5114918947219849",
        "ggslimit": "500",
        "ggsradius": "1000",
        "action": "query",
        "prop": "coordinates|pageterms|pageimages",
    }


class TestWikipediaAPI(unittest.TestCase):

    def setUp(self):
        self.api = WikipediaAPI(USER_DETAILS, QUERY)

    def test_send_query(self):
        """test response from sending query"""
        response = self.api._send_query()
        pprint(response)
        assert isinstance(response, dict)
        assert 'query' in response.keys()

    def test_next_search_results(self):
        """test result pagination"""
        response = self.api._send_query()
        old_page = None
        for page in self.api._next_search_results(response):
            pprint(page)
            assert page != old_page
            assert 'continue' in page.keys() or 'batchcomplete' in page.keys()
            old_page = page

    def test_get_data(self):
        """test get all pages"""
        data = self.api.get_data()
        keys = ['index', 'coordinates', 'ns', 'pageid', 'terms', 'title']
        assert isinstance(data, dict)
        pprint(data)
        for page, result in data.items():
            assert all([key in result.keys() for key in keys])