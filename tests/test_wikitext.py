from wikigeo.wikisource.wikitext import scrape_page_text
import time

def test_scrape():
    limit = 1000
    result = scrape_page_text('Berlin', limit, 'de')
    print(result)
    assert isinstance(result['text'], str) and len(result['text']) <= limit
