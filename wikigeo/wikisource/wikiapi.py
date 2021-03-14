"""Querying Wikipedia's APIs"""
import logging
import time
from typing import Iterator
import requests_html as r


class WikipediaAPI():

    """sends queries to the Wikipedia API
    language options and stats can be found here: https://en.wikipedia.org/wiki/List_of_Wikipedias"""

    def __init__(self, userinfo: str, query: dict, language: str = "en"):
        self.headers = {"User-agent": userinfo}
        self.session = r.HTMLSession()
        self.url = f"https://{language}.wikipedia.org/w/api.php"
        self.query = query

    def _send_query(self) -> dict:
        """sends a query and returns response"""

        logging.debug("sending query: %s", self.query)
        response = self.session.get(self.url, params=self.query, headers=self.headers)
        logging.debug(response)
        if not response.ok:
            raise Exception(response)
        result = response.json()
        try:
            logging.warning(result["error"])
            raise Exception("Check parameters; " + str(self.data))
        except KeyError:
            return result

    def _next_search_results(self, result: dict) -> Iterator[dict]:
        """get next set of results for query response"""
        yield result
        while "continue" in result.keys():
            logging.debug("getting next page from %s", result["continue"])
            # adding continue parameters to query
            for cont_param, value in result["continue"].items():
                self.query[cont_param] = value
            next_result = self._send_query()
            time.sleep(1)
            yield next_result
            # checking if new results are the same as the previous
            if next_result == result:
                logging.debug("got same results")
                break
            result = next_result
        if "batchcomplete" in result.keys():
            logging.debug("batchcomplete")
        else:
            logging.warning("continue not in new batch")

    def get_data(self) -> dict:
        """return all data from search"""
        first_page = self._send_query()
        all_results = [page for page in self._next_search_results(first_page)]
        combined_results = {}
        for result in all_results:
            for article, data in result["query"]["pages"].items():
                # updating the old results
                if article not in combined_results.keys():
                    combined_results[article] = data
                else:
                    combined_results[article].update(data)
        return combined_results


def query_search_nearby(lat: float, lon: float, limit: int, radiusmetres: int) -> dict:
    """query to get wiki pages near a coordinate
    options for geosearch are found here:
    https://en.wikipedia.org/w/api.php?action=help&modules=query+geosearch"""

    if not 10 <= radiusmetres <= 10000:
        raise Exception(
            "Check parameters; radiusmetres must be an int between 10 and 10000"
        )
    if not 0 < limit <= 500:
        raise Exception("Check parameters; limit must be an int between 1 and 500")

    query = {
        "format": "json",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggslimit": f"{limit}",
        "ggsradius": f"{radiusmetres}",
        "action": "query",
        "prop": "coordinates|pageterms|pageimages",
    }

    return query

def query_search_string(search_string, limit=5) -> dict:
    """query to search wikipedia for pages containing search string.
    options for search found here: https://www.mediawiki.org/wiki/API:Search
    and for query here: https://www.mediawiki.org/wiki/API:Query"""

    if not isinstance(search_string, str):
        raise Exception("Check parameters; keyword must be a string")
    if (not isinstance(limit, int)) or (not 0 < limit <= 500):
        raise Exception("Check parameters; limit must be an int between 1 and 500")

    query = {
        "format": "json",
        "generator": "search",
        "gsrsearch": search_string.replace(" ", "+"),
        "gsrlimit": f"{limit}",
        "colimit": f"{limit}",
        "action": "query",
        "prop": "coordinates|pageterms|pageimages",
        "piprop": "original|name",
        "coprop": "type",
        "coprimary": "primary",
    }
    
    return query

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


class WikiCommonsAPI(WikipediaAPI):

    """sends queries to the wiki commons api"""

    def __init__(self, userinfo):
        super().__init__(userinfo)
        self.url = "https://commons.wikimedia.org/w/api.php"

    def search_nearby(self, lat, lon, radiusmetres):
        """get images near given coordinates from wikimedia commons.
        options for image info are found here:
         https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bimageinfo"""

        if not isinstance(lat, float):
            raise Exception("Check parameters; latitude must be a float")
        if not isinstance(lon, float):
            raise Exception("Check parameters; longitude must be a float")
        if (not isinstance(radiusmetres, int)) or (not 10 <= radiusmetres <= 10000):
            raise Exception(
                "Check parameters; radiusmetres must be an int between 10 and 10000"
            )

        self.query = {
            "format": "json",
            "action": "query",
            "generator": "geosearch",
            "ggscoord": "{}|{}".format(lat, lon),
            "ggslimit": 5,
            "prop": "imageinfo|imagelabels|coordinates",
            "iilimit": 1,
            "iiprop": "url|extmetadata",
            "iiurlwidth": "250",
            "iiurlheight": "250",
            "ggsradius": "{}".format(radiusmetres),
            "ggsnamespace": "6",
        }
        response = self._send_query()
        self._next_search_results(response)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    lat = 51.477106480966924
    lon = -0.05733484162192326
    limit = 50
    radiusmetres = 1000

    #wiki = WikiCommonsAPI("")
    #wiki.search_nearby(coords[0], coords[1], 10000)
    #pprint(wiki.return_data())

    query = {
        "format": "json",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggslimit": f"{limit}",
        "ggsradius": f"{radiusmetres}",
        "action": "query",
        "prop": "coordinates|pageterms|pageimages",
    }
    wiki = WikipediaAPI("testing", query)
    result = wiki._send_query()
    data = {}
    for page in wiki._next_search_results(result):
        print(page["query"]["pages"]['56738761'])
        data.update(page)
    print(len(data["query"]["pages"]))
    print(data["query"]["pages"].keys())
    print(data["query"]["pages"]['56738761'])
