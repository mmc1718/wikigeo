import logging
import math
from pprint import pprint
from fuzzywuzzy import fuzz
from wikigeo.wikisource.wikiapi import WikipediaAPI, query_nearby, query_by_string, query_commons_nearby
from wikigeo.wikisource.wikitext import scrape_page_text


class WikiExtractor:

    """

    Search wikipedia and return specified information.

    """

    def __init__(self, language: str, userinfo: str):
        self.user = userinfo
        self.language = language
        self.api = WikipediaAPI("test")
        self.commonsapi = WikipediaAPI("test", commons=True)

    def get_nearby_pages(self, lat: float, lon: float, limit: int = 4, radiusmeters: int = 10000):
        """

        Get details for all pages within a given radius of given coordinates.

        radiusmeters: the distance in metres to search, can be max 10000 (10km).
         default is 10000

        limit: max number of pages to return (default 4)

        returns list of dictionaries with title, label, description, coordinates, image

        """

        titles = []
        labels = []
        descriptions = []
        coordinates = []
        images = []
        query = query_nearby(lat, lon, limit, radiusmeters)
        response = self.api.get_data(query)
        for _, result in response.items():
            titles.append(result["title"])
            try:
                labels.append(result["terms"]["label"])
            except KeyError:
                labels.append(None)
            try:
                descriptions.append(result["terms"]["description"])
            except KeyError:
                descriptions.append(None)
            coordinates.append(
                {
                    "lat": result["coordinates"][0]["lat"],
                    "lon": result["coordinates"][0]["lon"],
                }
            )
            try:
                thumbnail = result["thumbnail"]["source"]
                image = thumbnail.split("/")
                image.pop(-1)
                image.remove("thumb")
                imageurl = "/".join(image)
                images.append(imageurl)
            except KeyError:
                images.append(None)
            output = [
                {
                    "title": title,
                    "description": description,
                    "coordinates": latlon,
                    "label": label,
                    "image": image,
                }
                for title, description, latlon, label, image in zip(
                    titles, descriptions, coordinates, labels, images
                )
            ]
            return output

    def get_page_text(self, pagetitle, limit=False):
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
        self, lat, lon, radiusmeters=10000, nametomatch=False, matchfilter=False
    ):
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
            raise Exception("nametomatch must be set to a name if using a matchfilter")
        query = query_commons_nearby(lat, lon, radiusmeters)
        response = self.commonsapi.get_data(query)
        imagedata = []
        images = response
        for _, value in images.items():
            image = value.get("imageinfo", {})[0].get("url", "")
            title = value.get("title", "")
            url = value.get("imageinfo", {})[0].get("descriptionurl", "")
            lat = value["coordinates"][0]["lat"]
            lon = value["coordinates"][0]["lon"]
            imagelicense = (
                value.get("imageinfo", {})[0]
                .get("extmetadata", {})
                .get("License", {})
                .get("value", "")
            )
            author = (
                value.get("imageinfo", {})[0]
                .get("extmetadata", {})
                .get("Attribution", {})
                .get("value", "")
            )
            description = (
                value.get("imageinfo", {})[0]
                .get("extmetadata", {})
                .get("ImageDescription", {})
                .get("value", "")
            )
            imagedata.append(
                {
                    "image": image,
                    "title": title,
                    "url": url,
                    "lat": lat,
                    "lon": lon,
                    "author": author,
                    "license": imagelicense,
                    "description": description,
                }
            )
        logging.debug(imagedata)
        if nametomatch and any(imagedata):
            # print('nametomatch is ' + str(nametomatch))
            # print('imagedata is ' + str(imagedata))
            logging.debug("matching on name...")
            for image in imagedata:
                image["name match"] = fuzz.partial_ratio(
                    nametomatch.lower(), image["title"].lower()
                )
            imagedata.sort(key=lambda x: int(x["name match"]), reverse=True)
        if matchfilter and any(imagedata):
            imagedata = [
                image for image in imagedata if image["name match"] > matchfilter
            ]
        return imagedata

    def _get_km_distance(self, lat1, lon1, lat2, lon2):
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

    def get_page_match(
        self, keyword, searchlat, searchlon, bestmatch, maxdistance=30, minnamematch=0
    ):
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

        minnamematch: int, results must have a higher name match than
        minnamematch, between 0-100
                    (default 50)

        returns a (list of) dictionaries containing page title, description,
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
        logging.debug(search_results)
        try:
            logging.debug("results: %s", str(len(search_results["query"]["pages"])))
        except:
            logging.warning("cannot find data from %s", str(search_results))
            return {}
        for _, info in search_results["query"]["pages"].items():
            name = info["title"]
            logging.debug("found %s", name)
            try:
                lat = info["coordinates"][0]["lat"]
                lon = info["coordinates"][0]["lon"]
            except:
                logging.debug("cannot find coords for %s", name)
                logging.debug(info)
                continue
            try:
                description = info["terms"]["description"]
            except:
                logging.debug("cannot find description for %s", name)
                description = None
            try:
                label = info["terms"]["label"]
            except:
                logging.debug("cannot find label for %s", name)
                label = None
            try:
                image = info["original"]["source"]
            except:
                logging.debug("cannot find image for %s", name)
                image = None
            result = {
                "title": name,
                "description": description,
                "label": label,
                "image": image,
                "lat": lat,
                "lon": lon,
            }
            result["distance"] = self._get_km_distance(searchlat, searchlon, lat, lon)
            result["name match"] = fuzz.ratio(name.lower(), keyword.lower())
            # result['summary'] = self.getPageText([name])['text'][0:200]
            data.append(result)
        logging.debug("final data length: %s", str(len(data)))
        logging.debug("results with coords saved from wiki search: %s", str(len(data)))
        # filtering for relevant results
        # results = [place for place in data if ((place['distance'] < 10 and
        # place['name match'] > 50) or (place['name match'] > 65 and
        # place['distance'] < 30) or (place['distance'] < 5))]
        results = [
            place
            for place in data
            if (
                (place["distance"] < maxdistance)
                and (place["name match"] > minnamematch)
            )
        ]
        if results:
            # getting best match if requested
            if bestmatch == "name":
                results.sort(key=lambda result: int(result["name match"]), reverse=True)
                logging.debug("wikis: %s", str(results))
                return results[0]
            if bestmatch == "distance":
                results.sort(key=(lambda result: abs(result["distance"])))
                logging.debug("wikis: %s", str(results))
                return results[0]
            return results
        return {}
