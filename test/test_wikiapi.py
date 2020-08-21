from wikigeo.wikisource.wikiapi import WikipediaAPI, WikiCommonsAPI

class TestWikiapi:

    def test_search_nearby(self):
        wiki = WikipediaAPI("testing marymcguire1718@gmail.com")
        wiki.search_nearby(51.43295, -0.5114918947219849, 10, 10000)
        result = wiki.return_data()
        print(result)
        assert isinstance(result['query']['pages'], dict)

    def test_search_string(self):
        wiki = WikipediaAPI("testing marymcguire1718@gmail.com")
        wiki.search_string('Staines Bridge', limit=5)
        result = wiki.return_data()
        print(result)
        assert isinstance(result['query']['pages'], dict)

    def test_commons_search_nearby_result(self):
        commons = WikiCommonsAPI("testing marymcguire1718@gmail.com")
        commons.search_nearby(51.43295, -0.5114918947219849, 1000)
        result = commons.return_data()
        print(result)
        assert isinstance(result['query']['pages'], dict)

    def test_commons_search_nearby_noresult(self):
        commons = WikiCommonsAPI("testing marymcguire1718@gmail.com")
        commons.search_nearby(45.78024, -34.91654, 1000)
        result = commons.return_data()
        print(result)
        assert isinstance(result, dict)

