import pytest
from wikigeo import WikiExtractor


def test_get_nearby_images():
    wiki = WikiExtractor(language='en', userinfo="test")
    images = wiki.get_nearby_images(55.95527, -3.18108, nametomatch='Calton Hill', matchfilter=40)
    for result in images:
        assert isinstance(result, dict) and isinstance(result['image'], str)

def test_get_page_match():
    wiki = WikiExtractor(language='en', userinfo="test")
    suggested = wiki.get_page_match("Staines Moor", 51.43260, -0.51074, bestmatch=False, maxdistance=100)
    for page in suggested:
        assert isinstance(page['title'], str)

def test_get_page_text():
    wiki = WikiExtractor(language='en', userinfo="test")
    page = wiki.get_page_text('Staines Bridge', limit=500, translateto='de')
    assert isinstance(page['text'][0], str) and len(page['text']) == 1

def test_get_nearby_pages():
    wiki = WikiExtractor(language='en', userinfo="test")
    data = wiki.get_nearby_pages(54.6687, -7.6823)
    for page in data:
        assert isinstance(page['title'], str) and isinstance(page['coordinates']['lat'], float)
