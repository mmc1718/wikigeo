"""scrape and parse text from wikipedia pages (quicker than using the parse api)"""
import logging
from requests_html import HTMLSession


def scrape_page_text(pagetitle: str, char_limit: int, wiki_lang: str = "en") -> dict:
    """returns text on a given wikipedia page.

    pagetitle: string of the extact page title"""

    url = f"https://{wiki_lang}.wikipedia.org/wiki/"
    session = HTMLSession()
    page_url = url + pagetitle.replace(' ', '_')
    response = session.get(page_url)
    logging.debug(response)
    if not response.ok:
        raise Exception('error response: ' + response)
    page = response.html
    page_text = [elem.text for elem in page.find('p, h2, h3')]
    page_text = ' '.join(page_text).replace('[edit]', '')
    if char_limit:
        result = {'title': pagetitle, 'text': page_text[:char_limit]}
    else:
        result = {'title': pagetitle, 'text': page_text}
    return result
