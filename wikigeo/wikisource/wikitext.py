from requests_html import HTML, HTMLSession
import time
from googletrans import Translator
import logging

class WikiText(object):

    """methods to scrape and parse text from wikipedia pages
    (quicker than using the parse api)"""

    def __init__(self, limit, language='en'):
        self.wikidomain = 'https://{}.wikipedia.org/wiki/'.format(language)
        self.data = {}
        self.language = language
        self.translator = Translator()
        self.limit = limit
        if(not isinstance(self.limit, int)):
            raise Exception('invalid limit argument; must be False or int')
    
    def scrape_page_text(self, pagetitle):
        """returns text on a given wikipedia page. 

        pagetitle: string of the extact page title"""

        session = HTMLSession()
        url = self.wikidomain + pagetitle.replace(' ', '_')
        response = session.get(url)
        if(not response.ok):
            raise Exception('error response:' + response)
        logging.debug(response)
        page = response.html
        pagetext = [elem.text for elem in page.find('p, h2, h3')]
        pagetext = ' '.join(pagetext).replace('[edit]', '')
        if(self.limit):
            result = {'title': pagetitle, 'text': pagetext[0:self.limit]}
        else:
            result = {'title': pagetitle, 'text': pagetext}
        return result

    def translate_text(self, textlist, translateto):
        """translates text into the specified language. 
        e.g. if using the french (fr) wikipedia, can translate results into english by setting
         translateto='en'
         textlist: a list of strings to be translated. each string must be under 10000 chars
         returns a list of strings of translated text"""
        
        for extract in textlist:
            if(len(extract) > 10000):
                raise Exception('Texts over 10000 chars are not reliably translated. Please use limit parameter.')
        translations = self.translator.translate(textlist, dest=translateto, src=self.language)
        if(self.limit):
            result = [translation.text[0:self.limit] for translation in translations]
        else:
            result = [translation.text for translation in translations]
        return result

