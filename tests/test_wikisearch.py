import unittest
from wikigeo import WikiExtractor


class TestWikiExtractor(unittest.TestCase):
    def setUp(self):
        self.wiki = WikiExtractor("en", "test")

    def test_get_nearby_images(self):
        """test format of nearby images result"""
        images = self.wiki.get_nearby_images(
            55.95527, -3.18108, nametomatch="Calton Hill", matchfilter=40
        )
        assert len(images) == 2
        for key, result in images.items():
            print(result)
            assert (
                isinstance(result, dict)
                and isinstance(result["image"], str)
                and isinstance(result["lat"], float)
                and isinstance(result["lon"], float)
            )

    def test_get_nearby_images_none(self):
        """test empty results when no images found"""
        images = self.wiki.get_nearby_images(
            58.076026212,
            1.730324014,
            nametomatch="Norwegian Boundary Sediment Plain",
            matchfilter=44,
        )
        assert len(images) == 0

    def test_get_page_match(self):
        """test format and number of page keyword matches"""
        suggested = self.wiki.get_page_match(
            "Staines Moor", 51.43260, -0.51074, bestmatch=False, maxdistance=100
        )
        assert "page_matches" in suggested.keys()
        results = suggested["page_matches"]
        assert len(results) == 3
        for page in results:
            assert isinstance(page["title"], str)

    def test_get_nearby_pages(self):
        """test format and number of pages near given point"""
        data = self.wiki.get_nearby_pages(54.6687, -7.6823)
        assert len(data) == 4
        for page in data:
            assert isinstance(page["title"], str) and isinstance(
                page["coordinates"]["lat"], float
            )

    def test_get_page_text(self):
        """test text from page returned"""
        page = self.wiki.get_page_text("Staines Bridge", limit=500)
        for key in ["title", "text"]:
            assert key in page.keys()
        assert isinstance(page["text"][0], str) and len(page["text"]) == 500

    def test_get_page_match_case_two(self):
        """test format of keyword page match"""
        suggested = self.wiki.get_page_match(
            "Staines",
            51.43399588542416,
            -0.5114918947219849,
            bestmatch=False,
            maxdistance=30,
        )
        assert "page_matches" in suggested.keys()
        results = suggested["page_matches"]
        assert len(results) == 1
        for page in results:
            assert isinstance(page["title"], str)
