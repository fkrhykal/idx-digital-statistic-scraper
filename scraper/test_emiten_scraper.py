from unittest import TestCase
from scraper.emiten_scraper import get_emitens


class TestEmitenScraper(TestCase):

    def test_get_emitens(self):
        response = get_emitens()
        self.assertIsNotNone(response)
        self.assertIsInstance(response["data"], list)
