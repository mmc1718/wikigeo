import requests_html as r
from requests_html import HTML
import json
import time
from pprint import pprint
from wikiapi import Wikipedia, WikiCommons
import logging
from fuzzywuzzy import fuzz
import math


# hits wiki with no delays between requests, seems to be ok but might want to check limits


class WikiExtractor(object):

    """searches wikipedia and returns specified information"""

    def __init__(self, language, userinfo):
        self.wiki = Wikipedia(userinfo, language=language)
        self.commons = WikiCommons(userinfo)

    def getNearbyPages(self, lat, lon, toget=['titles'], limit=4, radiusmetres=10000):
        """returns requested info for all pages nearby given coordinates.
        options toget: titles, labels, descriptions, coordinates, images
        returns: dictionary of arrays for each requested info"""
        titles = []
        labels = []
        descriptions = []
        coordinates = []
        images = []
        self.wiki.search_nearby(lat, lon, limit, radiusmetres)
        response = self.wiki.return_data()
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


    def getPageText(self, pagetitle):
        """gets the full text of a given page
        returns a dictionary with headers and text"""
        self.wiki.parse_page(pagetitle, ['text', 'sections'])
        response = self.wiki.return_data()
        try:
            page = HTML(html=response['parse']['text']['*'])
            pagetext = [para.text for para in page.find('p, h2, h3')]
            headerdata = response['parse']['sections']
            headers = [header['line'] for header in headerdata]
            result = {'headers': headers, 'text': ' '.join(pagetext).replace('[edit]', '')}
            return result
        except Exception:
            logging.debug('error while trying to parse ' + str(response))
            print('page cannot be found')
            return None

    def getNearbyImages(self, lat, lon, nametomatch=False, matchfilter=False):
        """gets all images nearby given coordinates from wiki commons.
        if nametomatch is set to a name then results are given a match rating against the name
        if matchfilter is set to an int then results are filtered for results that have a higher rated name match"""

        if(matchfilter and (not nametomatch)):
            raise Exception('nametomatch must be set to a name if using a matchfilter')
        self.commons.search_nearby(lat, lon)
        response = self.commons.return_data()
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


    def _getKmDistance(self, lat1, lon1, lat2, lon2):
        """converts decimal distance into kms"""
        latA = float(lat1) * math.pi / 180
        lngA = float(lon1) * math.pi / 180
        latB = float(lat2) * math.pi / 180
        lngB = float(lon2) * math.pi / 180
        distance = 6378 * math.acos(math.cos(latA) * math.cos(latB) * math.cos(lngB - lngA) + math.sin(latA) * math.sin(latB))
        return distance

    def getPageMatch(self, keyword, searchlat, searchlon, bestmatch='name'):
        """searches for matching wiki pages with locations by given keyword and location.
        returns description, images, coordinates, intro text and match rating.

        bestmatch: if 'name' will return best match based on name
                    if 'distance' will return best match on distance
                    if False will return all reasonable matches nearby

        Note: Works best for unique, proper names of geographically located places.
        Bases location on centrepoint, so very large/spread out entities likely won't match."""

        data = []
        self.wiki.search_string(keyword, limit=5)
        search_results = self.wiki.return_data()
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
            result['distance'] = self._getKmDistance(searchlat, searchlon, lat, lon)
            result['name match'] = fuzz.ratio(name, keyword)
            #result['summary'] = self.getPageText([name])['text'][0:200]
            data.append(result)
        logging.debug('final data length: ' + str(len(data)))
        logging.debug('results with coords saved from wiki search: ' + str(len(data)))
        # filtering for relevant results
        results = [place for place in data if ((place['distance'] < 10 and place['name match'] > 50) or (place['name match'] > 65 and place['distance'] < 30) or (place['distance'] < 5))]
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
    start = time.time()

    def run_getNearbyImages():
        titles = wiki.getNearbyImages(55.95527, -3.18108, nametomatch='Calton Hill', matchfilter=40)
        print(titles)
    
    def run_getPageMatch():
        suggested = wiki.getPageMatch("Staines Moor", 51.43260, -0.51074, bestmatch='name')
        print(suggested)

    def run_getPage():
        paras = wiki.getPage('Staines Bridge')
        print(paras)
    
    def run_getNearbyPages():
        data = wiki.getNearbyPages(54.6687, -7.6823, toget=['titles', 'coordinates', 'images'])
        print(data)
    

    run_getPageMatch()
    end = time.time()
    print('time taken:', end-start)
    