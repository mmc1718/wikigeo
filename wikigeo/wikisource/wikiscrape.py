from requests_html import HTML, HTMLSession
import time
from googletrans import Translator
import logging

class WikiScraper(object):

    """methods to scrape text wikipedia pages from wikipedia
    (quicker than using the parse api)"""

    def __init__(self, language='en'):
        self.wikidomain = 'https://{}.wikipedia.org/wiki/'.format(language)
        self.session = HTMLSession()
        self.data = {}
        self.language = language
        self.translator = Translator()
    
    def scrape_page_text(self, pagetitle, limit=False):
        """returns text on a given wikipedia page. 

        pagetitle: string of the extact page title
        limit: int representing character limit of returned text
                default is False (return all text)"""

        url = self.wikidomain + pagetitle.replace(' ', '_')
        response = self.session.get(url)
        if(not response.ok):
            raise Exception('error response:' + response)
        logging.debug(response)
        page = response.html
        pagetext = [elem.text for elem in page.find('p, h2, h3')]
        pagetext = ' '.join(pagetext).replace('[edit]', '')
        if(limit):
            result = {'title': pagetitle, 'text': pagetext[0:limit]}
        else:
            result = {'title': pagetitle, 'text': pagetext}
        return result

    def translate_text(self, textlist, translateto):
        """translates text into the specified language. 
        e.g. if using the french (fr) wikipedia, can translate results into english by setting
         translateto='en'
         textlist: a list of strings to be translated. each string must be under 10000 chars"""

        for extract in textlist:
            if(len(extract) > 10000):
                raise Exception('texts over 10000 chars are not reliably translated. Use limit parameter when scraping.')
        translations = self.translator.translate(textlist, dest=translateto, src=self.language)
        return [translation.text for translation in translations]


if __name__ == '__main__':

    wiki = WikiScraper('de')
    start = time.time()
    result = wiki.scrape_page_text('Berlin', limit=100)
    print(result)
    results = wiki.translate_text(['ich liebe Essen', 'Ich bin traurig'], 'en')
    print(results)
    end = time.time()
    print('time:' , end-start)