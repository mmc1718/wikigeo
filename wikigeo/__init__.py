import logging
from .wikimultisearch import WikiExtractor, ConcurrentSearcher

logger = logging.getLogger()
logging.basicConfig(filename='logging.log', level=logging.INFO)