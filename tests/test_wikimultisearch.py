import pytest
from wikigeo import ConcurrentSearcher

def test_nearby_pages():
    searcher = ConcurrentSearcher('en', "testing (marymcguire1718@gmail.com)")
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
        (50.86854995219705, -0.595084718328369)
    ]
    results = searcher.multi_nearby_pages(coords, limit=5, radiusmetres=8000)
    for result in results:
        print(result)
        assert isinstance(result['coords'], tuple) and isinstance(result['result'][0]['title'], str)

def test_page_text():
    searcher = ConcurrentSearcher('en', "testing (marymcguire1718@gmail.com)")
    titles = ['Staines-upon-Thames', 'Edinburgh', 'Killeter', 'Northern Ireland', 'Staines Moor', 
    'Epping Forest', 'France', 'Greater_London', 'Paris', 'Scotland', 'England', 'Manchester', 'Hyde Park', 
    'Birmingham', 'Surrey', 'Kent', 'South_East_England', 'Berkshire', 'City of London', 'Central_London']
    result = searcher.multi_page_text(titles, textlen=50)
    for page in result:
        assert isinstance(page['text'][0], str) and len(page['text']) == 50

def test_nearby_images():
    searcher = ConcurrentSearcher('en', "testing (marymcguire1718@gmail.com)")
    coords = [(55.94631, -3.16552), (51.43399588542416, -0.5114918947219849)]
    names = ["Edinburgh", False]
    imagesdata = searcher.multi_nearby_images(coords, names, matchfilter=40)
    for images in imagesdata:
        print(images)
        for result in images['result']:
            assert isinstance(result, dict) and isinstance(result['image'], str)

def test_page_match():
    searcher = ConcurrentSearcher('en', "testing (marymcguire1718@gmail.com)")
    searches = [('Staines', 51.43399588542416, -0.5114918947219849), ("Arthur's Seat", 55.94631, -3.16552)]
    matches = searcher.multi_page_match(searches, maxdistance=50, bestmatch=True, minnamematch=0)
    for page in matches:
        print(page)
        assert isinstance(page['result'][0]['title'], str) and isinstance(page['result'][0]['lat'], float)
    assert False
