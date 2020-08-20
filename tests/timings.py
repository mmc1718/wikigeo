from requests_html import HTML, HTMLSession
from wikigeo.wikisearch import WikiExtractor
import time
import wikipedia

# test speed for scraping instead of using parse api


wiki = WikiExtractor(language='en', userinfo="DaytripApp (marymcguire1718@gmail.com)")


def scrape():
    domain = 'https://en.wikipedia.org/wiki/'
    title = 'Central London'
    url = domain + title.replace(' ', '_')
    session = HTMLSession()
    response = session.get(url)
    print(response)
    page = response.html
    pagetext = [para.text for para in page.find('p, h2, h3')]
    pagetext = ' '.join(pagetext).replace('[edit]', '')
    result = {'text': pagetext}
    return result

def run_get_page_text():
    paras = wiki.get_page_text('Central London')
    return paras

def wiki_mod():
    ny = wikipedia.page('Central London')
    return ny.content

results_run = []
results_scrape = []
results_mod = []

for i in range(7):
    start = time.time()
    run_get_page_text()
    end = time.time()
    results_run.append(end-start)

    start = time.time()
    scrape()
    end = time.time()
    results_scrape.append(end-start)

    start = time.time()
    wiki_mod()
    end = time.time()
    results_mod.append(end-start)

print('average for run:', sum(results_run)/len(results_run))
print('average for scrape:', sum(results_scrape)/len(results_scrape))
print('average for mod:', sum(results_mod)/len(results_mod))

"""
current winner: scrape

average for run: 0.5450178214481899
average for scrape: 0.25179593903677805
average for mod: 0.6314457484654018
"""





