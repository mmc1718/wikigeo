# Wikigeo

Python library for supplementing geographic data with point of interest data from Wikipedia articles and Wikimedia Commons.

## Installation

pip install wikigeo

## Usage

### 1. Setting up wikiextractor

```python
from wikigeo import WikiExtractor

wiki = WikiExtractor('en', 'user details')
```

for language code options: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
for info on user details see: https://www.mediawiki.org/wiki/API:Etiquette#The_User-Agent_header


### 2. Getting all pages about places within a given distance (up to a max of 10km) from a given latitude longitude point:

```python
nearbypages = wiki.get_nearby_pages(51.43181, -0.51066, limit=4, radiusmetres=10000)
print(nearbypages)
```

returns dictionary of arrays for each requested info

### 3. Getting all images from Wikimedia Commons within a given radius (up to a max of 10km) of a given latitude longitude point:

```python
nearbyimages = wiki.get_nearby_images(51.44069, -0.56165, nametomatch='Runnymede', matchfilter=40)
print(nearbyimages)
```

returns list of dictionaries containing image details. Can match against a name (optional)

### 4. Finding the Wikipedia article for a given placename and location (result accuracy may vary):

```python
suggestedwiki = wiki.get_page_match("Runnymede", 51.44069, -0.56165, bestmatch=False, maxdistance=100)
print(suggestedwiki)
```

returns a (list of) dictionary(s) of suggested wiki pages that match. 
Optional: set bestmatch='name' or bestmatch='distance' to only select the best match on name/distance

### 5. Making multiple requests at once:

```python
from wikigeo import ConcurrentSearcher

coords = [(51.44069, -0.56165), (51.41016485685163, -0.6645655632019043)]

wiki = ConcurrentSearcher('en', 'user info')

nearby = wiki.multi_nearby_pages(coords)
print(nearby)
```

returns a list of dictionaries containing results


