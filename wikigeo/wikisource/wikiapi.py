"""Querying Wikipedia's APIs"""
import logging
import time
from typing import Iterator
import requests_html as r


class WikipediaAPI:

    """sends queries to the Wikipedia API
    language options and stats can be found here:
    https://en.wikipedia.org/wiki/List_of_Wikipedias"""

    def __init__(
        self, userinfo: str, commons: bool = False, language: str = "en"
    ):
        self.headers = {"User-agent": userinfo}
        self.session = r.HTMLSession()
        if commons:
            self.url = "https://commons.wikimedia.org/w/api.php"
        else:
            self.url = f"https://{language}.wikipedia.org/w/api.php"
        self.query = None

    def _send_query(self) -> dict:
        """sends query and returns response"""

        logging.debug("sending query: %s", self.query)
        response = self.session.get(self.url, params=self.query, headers=self.headers)
        logging.debug(response)
        if not response.ok:
            raise Exception(response)
        result = response.json()
        try:
            logging.warning(result["error"])
            raise Exception("Check parameters; " + str(result))
        except KeyError:
            return result

    def _next_search_results(self, result: dict) -> Iterator[dict]:
        """get next set of results for query response"""
        yield result
        while "continue" in result.keys():
            if "batchcomplete" in result.keys():
                logging.debug("batchcomplete and continue present")
                break
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

    def get_data(self, query: dict) -> dict:
        """return all data from search"""
        self.query = query
        first_page = self._send_query()
        all_results = self._next_search_results(first_page)
        combined_results = {}
        for result in all_results:
            for article, data in result["query"]["pages"].items():
                # updating the old results
                if article not in combined_results.keys():
                    combined_results[article] = data
                else:
                    combined_results[article].update(data)
        return combined_results


def query_nearby(
    lat: float, lon: float, limit: int, radiusmetres: int
) -> dict:
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


def query_by_string(search_string: str, limit: int = 5) -> dict:
    """query to search wikipedia for pages containing search string.
    options for search found here: https://www.mediawiki.org/wiki/API:Search
    and for query here: https://www.mediawiki.org/wiki/API:Query"""

    if not 0 < limit <= 500:
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


def query_parse_page(pagetitle: int, to_parse: list) -> dict:
    """query to parse a wiki page by page title.
    options for what to parse can be found here:
    https://www.mediawiki.org/wiki/API:Parsing_wikitext"""

    query = {
        "format": "json",
        "action": "parse",
        "page": "{}".format(pagetitle),
        "prop": "{}".format("|".join(to_parse)),
    }
    return query


def query_commons_nearby(lat: float, lon: float, radiusmetres: int) -> dict:
    """get images near given coordinates from wikimedia commons.
    options for image info are found here:
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bimageinfo"""

    if not 10 <= radiusmetres <= 10000:
        raise Exception(
            "Check parameters; radiusmetres must be an int between 10 and 10000"
        )

    query = {
        "format": "json",
        "action": "query",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggslimit": 5,
        "prop": "imageinfo|imagelabels|coordinates",
        "iilimit": 1,
        "iiprop": "url|extmetadata",
        "iiurlwidth": "250",
        "iiurlheight": "250",
        "ggsradius": f"{radiusmetres}",
        "ggsnamespace": "6",
    }
    return query
