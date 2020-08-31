# Wikigeo

Python library for supplementing geographic data with point of interest data from Wikipedia articles and Wikimedia Commons.

Wikigeo is a tool for retrieving information from Wikipedia articles and Wikimedia Commons relating to points of interests.

Given pairs of longitude and latitude coordinates you can use Wikigeo to search for Wikipedia articles and images near that point, as well as find articles related to a particular place of interest. This tool is designed to be suitable for e.g. adding data to (Geo)Dataframes.

## Installation

```
pip install wikigeo
```

## Usage

### 1. Setting up wikiextractor

```python
>>>from wikigeo import WikiExtractor
>>>
>>>wiki = WikiExtractor('en', 'user details')
```

+ for language code options: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
+ for info on user details see: https://www.mediawiki.org/wiki/API:Etiquette#The_User-Agent_header


### 2. Getting all pages about places within a given distance (up to a max of 10km) from a given latitude longitude point:

```python
>>>nearbypages = wiki.get_nearby_pages(51.43181, -0.51066, limit=4, radiusmetres=10000)
>>>
>>>print(nearbypages)
[{'title': 'River Colne, Hertfordshire', 'description': ['river in Hertfordshire, England'], 'coordinates': {'lat': 51.43305556, 'lon': -0.51527778}, 'label': ['River Colne'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/8/8f/RiverColneStaines01.JPG'}]
```

### 3. Getting all images from Wikimedia Commons within a given radius (up to a max of 10km) of a given latitude longitude point:

```python
>>>nearbyimages = wiki.get_nearby_images(51.44069, -0.56165, nametomatch='Runnymede', matchfilter=40)
>>>
>>>print(nearbyimages)
[{'image': 'https://upload.wikimedia.org/wikipedia/commons/8/80/Langham_Pond%2C_Runnymede_-_geograph.org.uk_-_276735.jpg', 'title': 'File:Langham Pond, Runnymede - geograph.org.uk - 276735.jpg', 'url': 'https://commons.wikimedia.org/wiki/File:Langham_Pond,_Runnymede_-_geograph.org.uk_-_276735.jpg', 'name match': 100}]
```


### 4. Finding the Wikipedia article for a given placename and location (result accuracy may vary):

```python
>>>suggestedwiki = wiki.get_page_match("Runnymede", 51.44069, -0.56165, bestmatch=False, maxdistance=100)
>>>
>>>print(suggestedwiki)
[{'title': 'Borough of Runnymede', 'description': ['local government district with borough status in Surrey, England'], 'label': ['Runnymede'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/7/79/Runnymede_UK_locator_map.svg', 'lat': 51.395, 
'lon': -0.541, 'distance': 5.284246482529435, 'name match': 62}, {'title': 'Runnymede', 'description': ['water-meadow alongside the River Thames in Surrey, England'], 'label': ['Runnymede'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/5/55/RunnymedeMagnacartaisle.jpg', 'lat': 51.44444444, 'lon': -0.56527778, 'distance': 0.4878789100654987, 'name match': 100}] 
```

+ Optional: set bestmatch='name' or bestmatch='distance' to only select the best match on name/distance

### 5. Making multiple requests at once:

```python
>>>from wikigeo import ConcurrentSearcher
>>>
>>>coords = [(51.44069, -0.56165), (51.41016485685163, -0.6645655632019043)]
>>>
>>>wiki = ConcurrentSearcher('en', 'user info')
>>>nearby = wiki.multi_nearby_pages(coords)
>>>
>>>print(nearby)
[{'coords': (51.44069, -0.56165), 'result': [{'title': 'Runnymede', 'description': ['water-meadow alongside the River Thames in Surrey, England'], 'coordinates': {'lat': 51.44444444, 'lon': -0.56527778}, 'label': ['Runnymede'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/5/55/RunnymedeMagnacartaisle.jpg'}]}, {'coords': (51.41016485685163, -0.6645655632019043), 'result': [{'title': 'Ascot, Berkshire', 'description': ['affluent small town in east Berkshire, England'], 'coordinates': {'lat': 51.4084, 'lon': -0.6707}, 'label': ['Ascot'], 'image': 'https://upload.wikimedia.org/wikipedia/commons/7/71/Geograph_1851274_5a75705a_High_Street%2C_Ascot.jpg'}]}]
```


