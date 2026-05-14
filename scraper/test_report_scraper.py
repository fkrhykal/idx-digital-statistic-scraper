from unittest import TestCase
from scraper.report_scraper import get_inlineXBRL_attachments, get_inlineXBRL_zip_files, save_inlineXBRL_zip_files
from cloudscraper import CloudScraper
from pathlib import Path


class ReportScaperTest(TestCase):

    def setUp(self):
        super().setUp()
        self.scraper = CloudScraper()

    def tearDown(self):
        super().tearDown()
        self.scraper.close()

    def test_get_inlineXBRL_attachments(self):
        attachments = get_inlineXBRL_attachments(self.scraper, page_size=1, report_type='fs')
        
        for attachment in attachments:
            filepath = attachment['File_Path']
            self.assertTrue(filepath.endswith('inlineXBRL.zip'))
    
    def test_get_inlineXBRL_zip_file(self):
        attachments = list(get_inlineXBRL_attachments(self.scraper, page_size=1))
        files = list(get_inlineXBRL_zip_files(self.scraper, attachments))
        self.assertEqual(len(attachments), len(files))

    def test_save_inlineXBRL_zip_file(self):
        attachments = get_inlineXBRL_attachments(self.scraper, page_size=1)
        files = get_inlineXBRL_zip_files(self.scraper, attachments)
        filepaths = save_inlineXBRL_zip_files(Path.cwd() / 'temp', files)
        for filepath in filepaths:
            self.assertTrue(Path(filepath).exists())


        
            