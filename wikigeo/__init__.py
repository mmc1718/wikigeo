import logging
from wikigeo.wikimultisearch import WikiExtractor, ConcurrentSearcher

logger = logging.getLogger()
logging.basicConfig(filename='logging.log', level=logging.INFO)