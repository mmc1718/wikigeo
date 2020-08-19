import requests_html as r
from requests_html import HTML
import json
import time
from pprint import pprint
from wikiapi import WikipediaAPI, WikiCommonsAPI
from wikiscrape import WikiScraper
import logging
from fuzzywuzzy import fuzz
import math


# sort out logging v print


class WikiExtractor(object):

    """methods to search wikipedia and return specified information"""

    def __init__(self, language, userinfo):
        self.user = userinfo
        self.language = language

    def get_nearby_pages(self, lat, lon, toget=['titles'], limit=4, radiusmetres=10000):
        """get requested info for all pages nearby given coordinates.

        radiusmeters: the distance in metres to search, can be max 10000 (10km). default is 10000
        limit: max number of pages to return (default 4)
        toget: list containing any of 'titles', 'labels', 'descriptions', 'coordinates', 'images' 
        (default ['titles'])

        returns dictionary of arrays for each requested info"""

        titles = []
        labels = []
        descriptions = []
        coordinates = []
        images = []
        wiki = WikipediaAPI(self.user, self.language)
        wiki.search_nearby(lat, lon, limit, radiusmetres)
        response = wiki.return_data()
        for page, result in response['query']['pages'].items():
            if('titles' in toget):
                titles.append(result['title'])
            if('labels' in toget):
                try:
                    labels.append(result['terms']['label'])
                except:
                    labels.append(None)
            if('descriptions' in toget):
                try:
                    descriptions.append(result['terms']['description'])
                except:
                    descriptions.append(None)
            if('coordinates' in toget):
                coordinates.append({'lat': result['coordinates'][0]['lat'], 'lon': result['coordinates'][0]['lon']})
            if('images' in toget):
                try:
                    thumbnail = result['thumbnail']['source']
                    image = thumbnail.split('/')
                    image.pop(-1)
                    image.remove('thumb')
                    imageurl = '/'.join(image)
                    images.append(imageurl)
                except:
                    images.append(None)
        data = {'titles': titles, 'labels': labels, 'descriptions': descriptions, 'coordinates': coordinates, 'images': images}
        output = {request: data[request] for request in toget}
        return output

    def get_page_text(self, pagetitle, limit=False, translateto=False):
        """scrape the full text of a given page
        returns a dictionary with pagetitle and text

        pagetitle: exact title of page to scrape
        limit: int, character limit of text returned"""
            
        wiki = WikiScraper(self.language)
        result = wiki.scrape_page_text(pagetitle, limit)
        if(translateto):
            result['text'] = wiki.translate_text([result['text']], translateto)
        return result

    """

    def get_page_textold(self, pagetitle, textlen=False):
        #gets the full text of a given page
        #returns a dictionary with headers and text
        
        #textlen: int representing character limit on text length in results. 
                #Default is False (return all text)

        wiki = WikipediaAPI(self.user, self.language)
        wiki.parse_page(pagetitle, ['text', 'sections'])
        response = wiki.return_data()
        try:
            page = HTML(html=response['parse']['text']['*'])
            pagetext = [para.text for para in page.find('p, h2, h3')]
            #headerdata = response['parse']['sections']
            #headers = [header['line'] for header in headerdata]
            pagetext = ' '.join(pagetext).replace('[edit]', '')
            if(textlen):
                #result = {'headers': headers, 'text': pagetext[0:textlen]}
                result = {'text': pagetext[0:textlen]}
            else:
                #result = {'headers': headers, 'text': pagetext}
                result = {'text': pagetext}
            return result
        except Exception:
            logging.warning('error while trying to parse ' + str(response))
            print('page cannot be found')
            return None
    """

    def get_nearby_images(self, lat, lon, radiusmetres=10000, nametomatch=False, matchfilter=False):
        """gets all images nearby given coordinates from wiki commons.

        radiusmetres: distance to search, max 10000 (10km)
        nametomatch: if set to a name then results are given a match rating against the name
        matchfilter: if set to an int then results are filtered for results that have a higher rated name match,
        can be between 0 (no matching) and 100 (exact match only)"""

        commons = WikiCommonsAPI(self.user)
        if(matchfilter and (not nametomatch)):
            raise Exception('nametomatch must be set to a name if using a matchfilter')
        commons.search_nearby(lat, lon, radiusmetres)
        response = commons.return_data()
        try:
            images = response['query']['pages']
            imagedata = []
            for key, value in images.items():
                image = value['imageinfo'][0]['url']
                title = value['title']
                url = value['imageinfo'][0]['descriptionurl']
                imagedata.append({'image': image, 'title': title, 'url': url})
        except KeyError:
            print('error while parsing ' + str(response))
        if(nametomatch):
            for image in imagedata:
                image['name match'] = fuzz.partial_ratio(nametomatch, image['title'])
            imagedata.sort(key=lambda x: int(x['name match']), reverse=True)
        if(matchfilter):
            imagedata = [image for image in imagedata if image['name match'] > matchfilter]
        return imagedata


    def _get_km_distance(self, lat1, lon1, lat2, lon2):
        """converts decimal distance into kms"""

        latA = float(lat1) * math.pi / 180
        lngA = float(lon1) * math.pi / 180
        latB = float(lat2) * math.pi / 180
        lngB = float(lon2) * math.pi / 180
        distance = 6378 * math.acos(math.cos(latA) * math.cos(latB) * math.cos(lngB - lngA) + math.sin(latA) * math.sin(latB))
        return distance

    def get_page_match(self, keyword, searchlat, searchlon, bestmatch, maxdistance=30, minnamematch=50):
        """searches for all geolocated wiki pages containing given keyword
        filters to results that are less than the maxdistance (default is 30km)

        bestmatch: if 'name' will return the best (highest on scale 0-100) match based 
                    on keyword matching page title
                    if 'distance' will return the best (closest) match on distance
                    if False will return all geolocated matches nearby
        maxdistance: int, results must be less than the max distance in km of results from search coords 
                    (default 30)
        minnamematch: int, results must have a higher name match than minnamematch, between 0-100 
                    (default 50)

        returns a (list of) dictionaries containing page title, description, label, image, distance, coords
        and match rating

        Note: Works best for unique, proper names of geographically located places.
        Bases location on centrepoint, so points on the edge of very large/spread out entities may not match."""

        data = []
        wiki = WikipediaAPI(self.user, self.language)
        wiki.search_string(keyword, limit=5)
        search_results = wiki.return_data()
        try:
            logging.debug('results: ' + str(len(search_results['query']['pages'])))
        except KeyError:
            logging.warning('cannot find data from ' + str(search_results))
        for page, info in search_results['query']['pages'].items():
            name = info['title']
            try:
                lat = info['coordinates'][0]['lat']
                lon = info['coordinates'][0]['lon']
            except KeyError:
                logging.debug('cannot find coords for ' + name)
                continue
            try:
                description = info['terms']['description']
            except KeyError:
                logging.debug('cannot find description for ' + name)
                description = None
            try:
                label = info['terms']['label']
            except KeyError:
                logging.debug('cannot find label for ' + name)
                label = None
            try:
                image = info['original']['source']
            except KeyError:
                logging.debug('cannot find image for ' + name)
                image = None
            result = {'title': name, 'description': description, 'label': label, 'image': image, 'lat': lat, 'lon': lon}
            result['distance'] = self._get_km_distance(searchlat, searchlon, lat, lon)
            result['name match'] = fuzz.ratio(name, keyword)
            #result['summary'] = self.getPageText([name])['text'][0:200]
            data.append(result)
        logging.debug('final data length: ' + str(len(data)))
        logging.debug('results with coords saved from wiki search: ' + str(len(data)))
        # filtering for relevant results
        #results = [place for place in data if ((place['distance'] < 10 and place['name match'] > 50) or (place['name match'] > 65 and place['distance'] < 30) or (place['distance'] < 5))]
        results = [place for place in data if (place['distance'] < maxdistance)]
        if(results):
            # getting best match if requested
            if(bestmatch == 'name'):
                results.sort(key=lambda result: int(result['name match']), reverse=True)
                logging.debug('wikis: ' + str(results))
                return results[0]
            elif(bestmatch == 'distance'):
                results.sort(key=(lambda result: abs(result['distance'])))
                logging.debug('wikis: ' + str(results))
                return results[0]
            else:
                return results
        else:
            return []


if __name__ == '__main__':

    wiki = WikiExtractor(language='en', userinfo="DaytripApp (marymcguire1718@gmail.com)")
    

    def run_get_nearby_images():
        titles = wiki.get_nearby_images(55.95527, -3.18108, nametomatch='Calton Hill', matchfilter=40)
        print(titles)
    
    def run_get_page_match():
        suggested = wiki.get_page_match("Staines Moor", 51.43260, -0.51074, bestmatch=False, maxdistance=100)
        print(suggested)

    def run_get_page_text():
        paras = wiki.get_page_text('Staines Bridge', limit=500, translateto='de')
        print(paras)
    
    def run_get_nearby_pages():
        data = wiki.get_nearby_pages(54.6687, -7.6823, toget=['titles', 'coordinates', 'images'])
        print(data)


    start = time.time()
    run_get_page_text()
    end = time.time()
    print('time taken:', end-start)
    