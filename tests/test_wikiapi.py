"""Test queries to Wikipedia API"""
import configparser
import unittest
from pprint import pprint
from wikigeo.wikisource.wikiapi import (
    WikipediaAPI,
    query_nearby,
    query_by_string,
    query_commons_nearby,
    query_parse_page,
)

config = configparser.ConfigParser()
config.read("config.ini")

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

QUERY_2 = {
    'format': 'json',
    'generator': 'geosearch',
    'ggscoord': '54.6687|-7.6823',
    'ggslimit': '4',
    'ggsradius': '10000',
    'action': 'query',
    'prop': 'coordinates|pageterms|pageimages'
}

class TestWikipediaAPI(unittest.TestCase):
    """ test Wikipedia API wrapper"""

    def setUp(self):
        self.api = WikipediaAPI(USER_DETAILS)

    def test_send_query(self):
        """test response from sending query"""
        self.api.query = QUERY
        response = self.api._send_query()
        pprint(response)
        assert isinstance(response, dict)
        assert "query" in response.keys()

    def test_send_query_2(self):
        """test response from sending query"""
        self.api.query = QUERY_2
        response = self.api._send_query()
        assert isinstance(response, dict)
        assert "query" in response.keys()

    def test_next_search_results(self):
        """test result pagination"""
        self.api.query = QUERY
        response = self.api._send_query()
        old_page = None
        for page in self.api._next_search_results(response):
            pprint(page)
            assert page != old_page
            assert "continue" in page.keys() or "batchcomplete" in page.keys()
            old_page = page

    def test_next_search_results_2(self):
        """test result pagination"""
        self.api.query = QUERY_2
        response = self.api._send_query()
        old_page = None
        for page in self.api._next_search_results(response):
            assert page != old_page
            assert "continue" in page.keys() or "batchcomplete" in page.keys()
            old_page = page

    def test_get_data(self):
        """test get all pages"""
        data = self.api.get_data(QUERY)
        keys = ["index", "coordinates", "ns", "pageid", "terms", "title"]
        assert isinstance(data, dict) and len(data) == 16
        for _, result in data.items():
            assert all(key in result.keys() for key in keys)

    def test_get_data_2(self):
        """test get all pages"""
        data = self.api.get_data(QUERY_2)
        keys = ["index", "coordinates", "ns", "pageid", "terms", "title"]
        assert isinstance(data, dict) and len(data) == 4
        for _, result in data.items():
            assert all(key in result.keys() for key in keys)


class TestQueries(unittest.TestCase):

    def test_query_nearby(self):
        """test query to search near given point"""
        query = query_nearby(54.6687, -7.6823, 4, 1000)
        api = WikipediaAPI(USER_DETAILS, "en")
        result = api.get_data(query)
        assert len(result.keys()) > 1

    def test_query_by_string(self):
        """test query to search page by string"""
        query = query_by_string("Staines Bridge", limit=5)
        api = WikipediaAPI(USER_DETAILS)
        result = api.get_data(query)
        keys = ["index", "ns", "pageid", "terms", "title"]
        assert isinstance(result, dict)
        pprint(result)
        for _, page in result.items():
            assert all(key in page.keys() for key in keys)

    def test_query_commons_nearby(self):
        """test query images near point"""
        query = query_commons_nearby(55.953251, -3.188267, 1000)
        api = WikipediaAPI(USER_DETAILS, commons=True)
        data = api.get_data(query)
        assert len(data) == 5
        for result, _ in data.items():
            assert "imageinfo" in data[result].keys()
