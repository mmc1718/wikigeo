# Wikigeo

Python library for supplementing geographic data with wiki data

# Installation

pip install wikigeo

# Usage

### 1. Setting up wikiextractor

from wikigeo import WikiExtractor

wiki = WikiExtractor('languagecode', 'userdetails')

for info on userdetails see: https://www.mediawiki.org/wiki/API:Etiquette#The_User-Agent_header
for language code options: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

### 2. Getting all pages within a given distance (up to a max of 10km) from a given latitude longitude point:

nearbypages = wiki.get_nearby_pages(latitude, longitude, limit=4, radiusmetres=10000)

returns dictionary of arrays for each requested info

### 3. Getting all images within a given radius (up to a max of 10km) of a given latitude longitude point:

nearbyimages = wiki.get_nearby_images(latitude, longitude, nametomatch, matchfilter=40)

returns list of dictionaries containing image details. Can match against a name (optional)

### 4. Finding the wikipedia page for a given placename and location (result accuracy may vary):

suggestedwiki = wiki.get_page_match("placename", lat, lon, bestmatch=False, maxdistance=100)

returns a (list of) dictionary(s) of suggested wiki pages that match. 
Optional only select the best match on name/distance

### 5. Find data for a list of coordinates:

coords = [(lat, lon), (lat, lon) ...]

from wikigeo import ConcurrentSearcher

wiki = ConcurrentSearcher(languagecode, userinfo)
nearby = wiki.multi_nearby_pages(coordpairs, limit=4, radiusmetres=10000)

returns a list of dictionaries containing results


