from django.test import TestCase
from crawler.scraping.scrapers import page_metas

import requests_mock

class PageMetasTestCase(TestCase):
    def setUp(self):
        self.fake_url = 'http://fake-url.com/super/article'
        self.fake_html = '''
        <html>
            <head>
                <title>Fake title</title>
                <meta name="preservation:priority" content="true"/>
                <meta name="preservation:release_date" content="2018-01-08"/>
                <meta name="preservation:notfound_only" content="false"/>
            </head>
        </html>
        '''

    def checkMetas(self, _):
        print("checkMetas %s" % _)
        [ title, metas ] = _
        self.assertEqual(len(metas), 3)
        self.assertEqual(title, 'Fake title')

    @requests_mock.Mocker()
    def test_scrape_metas(self, mock):
        mock.get(self.fake_url, text=self.fake_html)
        self.checkMetas(
            page_metas.scrape(self.fake_url)
        )

    def test_parse_metas(self):
        self.checkMetas(
            page_metas.parse(self.fake_html)
        )
