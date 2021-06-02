"""Processing data from Wikipedia APIs"""
import logging
import math
from fuzzywuzzy import fuzz
from wikigeo.wikisource.wikiapi import (
    WikipediaAPI,
    query_nearby,
    query_by_string,
    query_commons_nearby,
)
from wikigeo.wikisource.wikitext import scrape_page_text


def _get_km_distance(lat1, lon1, lat2, lon2) -> float:
    """converts decimal distance into kms"""

    lat_a = float(lat1) * math.pi / 180
    lng_a = float(lon1) * math.pi / 180
    lat_b = float(lat2) * math.pi / 180
    lng_b = float(lon2) * math.pi / 180
    distance = 6378 * math.acos(
        math.cos(lat_a) * math.cos(lat_b) * math.cos(lng_b - lng_a)
        + math.sin(lat_a) * math.sin(lat_b)
    )
    return distance


class WikiExtractor:
    """

    Search wikipedia and return specified information.

    """

    def __init__(self, language: str, userinfo: str):
        self.user = userinfo
        self.language = language
        self.api = WikipediaAPI("test")
        self.commonsapi = WikipediaAPI("test", commons=True)

    def get_nearby_pages(
        self, lat: float, lon: float, limit: int = 4, radiusmeters: int = 10000
    ) -> list:
        """

        Get details for all pages within a given radius of given coordinates.

        radiusmeters: the distance in metres to search, can be max 10000 (10km).
         default is 10000

        limit: max number of pages to return (default 4)

        returns list of dictionaries with title, label, description, coordinates, image

        """

        pages = []
        query = query_nearby(lat, lon, limit, radiusmeters)
        response = self.api.get_data(query)
        for _, result in response.items():
            page = {
                "title": result["title"],
                "description": None,
                "coordinates": {
                    "lat": result["coordinates"][0]["lat"],
                    "lon": result["coordinates"][0]["lon"],
                },
                "label": None,
                "image": None,
            }

            terms = result.get("terms")
            if terms is not None:
                page["label"] = terms.get("label")
                page["description"] = terms.get("description")

            thumbnail = result.get("thumbnail")
            if thumbnail is not None:
                thumbnail = thumbnail["source"]
                image = thumbnail.split("/")
                image.pop(-1)
                image.remove("thumb")
                imageurl = "/".join(image)
                page["image"] = imageurl

            pages.append(page)

        return pages

    def get_page_text(self, pagetitle: str, limit: bool = False) -> dict:
        """

        Retrieve the full text of a given page by page title.

        pagetitle: exact title of page to scrape

        limit: int, character limit of text returned.
        If set to False then the full text is returned. (default is False).

        returns a dictionary with pagetitle and text.

        """
        result = scrape_page_text(pagetitle, limit, self.language)
        return result

    def get_nearby_images(
        self,
        lat: float,
        lon: float,
        radiusmeters=10000,
        nametomatch=False,
        matchfilter=False,
    ) -> dict:
        """

        Gets all images nearby given coordinates from Wikimedia Commons.

        radiusmetres: distance to search, max 10000 (10km)

        nametomatch: if set to a string then results are given a match rating against the string.
         If False then no matching is done.

        matchfilter: if set to an int then results are filtered for results
        that have a higher rated name match,
        can be between 0 (no matching) and 100 (exact match only)

        returns list of dictionaries containing image data
        [{'image': i, 'title': t, 'url': url, 'name match': x}, ...]

        Note: if using matchfilter, nametomatch must be set to a string

        """
        if matchfilter and (not nametomatch):
            raise ValueError("nametomatch must be set to a name if using a matchfilter")
        query = query_commons_nearby(lat, lon, radiusmeters)
        response = self.commonsapi.get_data(query)
        imagedata = []
        i = 0
        for _, image in response.items():
            image_result = {
                "index": i,
                "image": "",
                "title": image.get("title", ""),
                "url": "",
                "lat": image["coordinates"][0]["lat"],
                "lon": image["coordinates"][0]["lon"],
                "author": "",
                "license": "",
                "description": "",
            }

            image_info = image.get("imageinfo")
            if image_info is not None:
                image_result["image"] = image_info[0].get("url", "")
                image_result["url"] = image_info[0].get("descriptionurl", "")

                metadata = image_info[0].get("extmetadata", {})
                if metadata is not None:
                    image_result["license"] = metadata.get("License", {}).get(
                        "value", ""
                    )
                    image_result["author"] = metadata.get("Attribution", {}).get(
                        "value", ""
                    )
                    image_result["description"] = metadata.get(
                        "ImageDescription", {}
                    ).get("value", "")
            i += 1
            imagedata.append(image_result)

        logging.debug("got image data as %s", imagedata)

        if nametomatch and any(imagedata):
            # sorting results by name match ratio
            logging.debug("matching on name...")
            for image in imagedata:
                image["name match"] = fuzz.partial_ratio(
                    nametomatch.lower(), image["title"].lower()
                )
            imagedata.sort(key=lambda x: int(x["name match"]), reverse=True)

            if matchfilter and any(imagedata):
                # filtering out matches below filter
                imagedata = [
                    image for image in imagedata if image["name match"] > matchfilter
                ]
        image_results = {i: image_result for i in range(len(imagedata)) for image_result in imagedata}
        return image_results

    def get_page_match(
        self,
        keyword: str,
        searchlat: float,
        searchlon: float,
        bestmatch: bool = False,
        maxdistance=30,
        name_match_greater=0,
    ) -> dict:
        """

        Searches for all geolocated wiki pages containing given keyword.
        Filters to results that are less than the maxdistance (default is 30km)

        bestmatch:

        bestmatch='name' will return the best (highest on scale 0-100) match based
        on keyword matching page title

        bestmatch='distance' will return the best (closest) match on distance

        bestmatch=False will return all geolocated matches nearby

        maxdistance: int, results must be less than the max distance
        in km of results from search coords
                    (default 30)

        name_match_greater: int, results must have a higher name match than
        name_match_greater, between 0-100
                    (default 50)

        returns a dictionary of page matches containing page title, description,
        label, image, distance, coords
        and match rating

        Note: Works best for unique, proper names of geographically
        located places (e.g. landmarks, buildings, parks)
        Bases location on centrepoint, so points on the edge of very large/spread
        out entities may not match.

        """
        data = []
        query = query_by_string(keyword.lower(), limit=3)
        search_results = self.api.get_data(query)

        for _, info in search_results.items():
            result = {
                "title": info["title"],
                "description": None,
                "label": None,
                "image": None,
                "lat": None,
                "lon": None,
                "distance": None,
                "name match": None,
            }
            logging.debug("found %s", result["title"])
            coordinates = info.get("coordinates")
            if coordinates is None:
                logging.debug("cannot find coords for %s", result["title"])
                logging.debug("full result: %s", info)
                continue

            result["lat"] = coordinates[0]["lat"]
            result["lon"] = coordinates[0]["lon"]

            terms = info.get("terms")
            if terms is not None:
                result["description"] = terms["description"]
                result["label"] = terms["label"]

            result["image"] = info.get("original", {}).get("source")
            result["distance"] = _get_km_distance(
                searchlat, searchlon, result["lat"], result["lon"]
            )
            result["name match"] = fuzz.ratio(result["title"].lower(), keyword.lower())
            data.append(result)

        logging.debug("final data length: %s", str(len(data)))
        logging.debug("results with coords saved from wiki search: %s", str(len(data)))
        # filtering for relevant results
        results = [
            place
            for place in data
            if (
                (place["distance"] < maxdistance)
                and (place["name match"] > name_match_greater)
            )
        ]
        if any(results):
            # getting top match if requested
            if bestmatch == "name":
                results.sort(key=lambda result: int(result["name match"]), reverse=True)
                logging.debug("wikis: %s", str(results))
                results = results[0]
            if bestmatch == "distance":
                results.sort(key=(lambda result: abs(result["distance"])))
                logging.debug("wikis: %s", str(results))
                results = results[0]
        return {"page_matches": results}
