from wikigeo.wikisource.wikitext import WikiText  
import time

class TestWikiscraper:

    def test_scrape(self):
        wiki = WikiText(100, 'de')
        start = time.time()
        result = wiki.scrape_page_text('Berlin')
        assert isinstance(result['text'], str) and len(result['text']) <= 100
    
    def translate_one(self):
        wiki = WikiText(100, 'de')
        testtext: """
        Berlin besitzt neben ausgedehnten Waldgebieten im Westen und Südosten des Stadtgebietes (Berliner Forsten) 
        viele große Parkanlagen. Da auch fast alle Straßen von Bäumen gesäumt sind, gilt Berlin als besonders grüne
         Stadt. In Berlin gibt es insgesamt rund 440.000 Straßenbäume, darunter 153.000 Linden, 82.000 Ahornbäume, 
         35.000 Eichen, 25.000 Platanen und 21.000 Kastanien.[25] Die über 2500 öffentlichen Grün-, Erholungs- und 
         Parkanlagen haben eine Gesamtfläche von über 5500 Hektar und bieten vielfältige Freizeit- und 
         Erholungsmöglichkeiten. Die größte heute als Park bezeichnete Anlage Berlins ist der Tempelhofer Park, der 
         auf dem ehemaligen Flughafen Tempelhof entstand. Im Zentrum der Stadt liegt der Große Tiergarten. Er ist die 
         älteste und mit 210 Hektar zweitgrößte und bedeutendste Parkanlage Berlins und wurde im Verlauf von mehr als 
         500 Jahren gestaltet. Ursprünglich ein ausgedehntes Waldareal vor den Toren der Stadt, genutzt von den 
         preußischen Adeligen als Jagd- und Ausrittgebiet, wurde dieses nach und nach von der Stadtentwicklung 
         umschlossen. Er erstreckt sich heute vom Bahnhof Zoo bis zum Brandenburger Tor und grenzt direkt an das 
         Regierungsviertel. Einige große Straßen durchschneiden den Tiergarten, darunter die Straße des 17. Juni als
          Ost-West-Achse. Sie kreuzen sich am Großen Stern, in dessen Mitte seit 1939 die Siegessäule steht. Der Große 
          Tiergarten hat die Gestalt einer naturnahen Parklandschaft: Charakteristisch sind die weiten, von kleinen 
          Wasserläufen durchzogenen und mit Baumgruppen bestandenen Rasenflächen sowie die Seen mit kleinen Inseln und 
          zahlreichen Brücken und Alleen. Anlagen wie der Englische Garten, die Luiseninsel und der Rosengarten setzen 
          an einigen Stellen schmuckgärtnerische Akzente.
        """
        results = wiki.translate_text([testtext], 'en')
        for result in results:
            assert isinstance(result, str) and len(result) <= 100
    
    def translate_many(self):
        wiki = WikiText(100, 'de')
        testtext: """
        Berlin besitzt neben ausgedehnten Waldgebieten im Westen und Südosten des Stadtgebietes (Berliner Forsten) 
        viele große Parkanlagen. Da auch fast alle Straßen von Bäumen gesäumt sind, gilt Berlin als besonders grüne
         Stadt. In Berlin gibt es insgesamt rund 440.000 Straßenbäume, darunter 153.000 Linden, 82.000 Ahornbäume, 
         35.000 Eichen, 25.000 Platanen und 21.000 Kastanien.[25] Die über 2500 öffentlichen Grün-, Erholungs- und 
         Parkanlagen haben eine Gesamtfläche von über 5500 Hektar und bieten vielfältige Freizeit- und 
         Erholungsmöglichkeiten. Die größte heute als Park bezeichnete Anlage Berlins ist der Tempelhofer Park, der 
         auf dem ehemaligen Flughafen Tempelhof entstand. Im Zentrum der Stadt liegt der Große Tiergarten. Er ist die 
         älteste und mit 210 Hektar zweitgrößte und bedeutendste Parkanlage Berlins und wurde im Verlauf von mehr als 
         500 Jahren gestaltet. Ursprünglich ein ausgedehntes Waldareal vor den Toren der Stadt, genutzt von den 
         preußischen Adeligen als Jagd- und Ausrittgebiet, wurde dieses nach und nach von der Stadtentwicklung 
         umschlossen. Er erstreckt sich heute vom Bahnhof Zoo bis zum Brandenburger Tor und grenzt direkt an das 
         Regierungsviertel. Einige große Straßen durchschneiden den Tiergarten, darunter die Straße des 17. Juni als
          Ost-West-Achse. Sie kreuzen sich am Großen Stern, in dessen Mitte seit 1939 die Siegessäule steht. Der Große 
          Tiergarten hat die Gestalt einer naturnahen Parklandschaft: Charakteristisch sind die weiten, von kleinen 
          Wasserläufen durchzogenen und mit Baumgruppen bestandenen Rasenflächen sowie die Seen mit kleinen Inseln und 
          zahlreichen Brücken und Alleen. Anlagen wie der Englische Garten, die Luiseninsel und der Rosengarten setzen 
          an einigen Stellen schmuckgärtnerische Akzente.
        """
        results = wiki.translate_text([testtext, testtext, testtext], 'en')
        for result in results:
            assert isinstance(result, str) and len(result) <= 100