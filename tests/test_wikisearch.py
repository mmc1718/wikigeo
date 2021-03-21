import unittest
import pytest
from wikigeo import WikiExtractor
from pprint import pprint
import logging


class TestWikiExtractor(unittest.TestCase):

    def setUp(self):
        self.wiki = WikiExtractor("en", "test")

    def test_get_nearby_images(self):
        images = self.wiki.get_nearby_images(55.95527, -3.18108, nametomatch='Calton Hill', matchfilter=40)
        for result in images:
            assert isinstance(result, dict) and isinstance(result['image'], str) and isinstance(result['lat'], float) and isinstance(result['lon'], float)

    def test_get_nearby_images_none(self):
        images = self.wiki.get_nearby_images(58.076026212, 1.730324014, nametomatch='Norwegian Boundary Sediment Plain', matchfilter=44)
        for result in images:
            print('result is ' + str(result))
            assert isinstance(result, dict)

    def test_get_page_match(self):
        suggested = self.wiki.get_page_match("Staines Moor", 51.43260, -0.51074, bestmatch=False, maxdistance=100)
        for page in suggested:
            assert isinstance(page['title'], str)

    def test_get_nearby_pages(self):
        data = self.wiki.get_nearby_pages(54.6687, -7.6823)
        for page in data:
            assert isinstance(page['title'], str) and isinstance(page['coordinates']['lat'], float)

    def test_get_page_text(self):
        page = self.wiki.get_page_text('Staines Bridge', limit=500)
        assert isinstance(page['text'][0], str) and len(page['text']) == 500

    def test_get_page_match_case_two(self):
        suggested = self.wiki.get_page_match('Staines', 51.43399588542416, -0.5114918947219849, bestmatch=False, maxdistance=30)
        for page in suggested:
            print(page) # debug
            assert isinstance(page['title'], str)