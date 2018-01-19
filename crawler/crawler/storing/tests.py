from django.test import TestCase
from crawler.storing import scrapers, utils
from crawler.constants import RESOURCE_TYPES
import requests_mock

class ScrapersTestCase(TestCase):
    def setUp(self):
        self.url = 'http://fake-url.com/my-post.html'
        self.img_url = 'http://fake-url.com/images/test.svg'
        self.img = '''
        <svg width="300" height="300">
            <g>
                <circle cx="150" cy="150" r="200" />
            </g>
        </svg>
        '''

        self.html = '''
        <html>
            <head>
                <link rel="stylesheet" href="styles/style.css" />
            </head>
            <body>
                <img src="images/test.svg" />
            </body>
        </html>
        '''
        self.css = '.test {}'
        self.style_url = 'http://fake-url.com/styles/style.css'

    def mockServer(self, m):
        m.register_uri('GET', self.img_url, text=self.img)
        m.register_uri('GET', self.url, text=self.html)
        m.register_uri('GET', self.style_url, text=self.css)
        return m

    def test_url_to_filename(self):
        url = 'http://test.com/a/file/to_test.png'
        fn = scrapers.url_to_filename(url)
        self.assertEqual(fn, 'to_test.png')

    @requests_mock.Mocker()
    def test_crawl_resource(self, m):
        m = self.mockServer(m)
        resource = scrapers.crawl_resource(self.url, 'styles/style.css')
        self.assertEqual(
            resource.get('url'),
            'styles/style.css'
        )
        self.assertEqual(
            resource.get('get_url'),
            self.style_url
        )

        self.assertEqual(
            resource.get('content').decode('utf-8'),
            self.css
        )
        self.assertEqual(
            resource.get('filename'),
            'style.css'
        )

    @requests_mock.Mocker()
    def test_crawl_page(self, m):
        m = self.mockServer(m)
        scraper = scrapers.HTMLScraper(self.url)
        self.assertEqual(
            scraper.html_content().decode('utf-8'),
            self.html
        )
        resources = scraper.static_resources()
        self.assertEqual(
            len(resources[RESOURCE_TYPES.STYLE]),
            1
        )

        self.assertEqual(
            len(resources[RESOURCE_TYPES.IMAGE]),
            1
        )

class UtilsTestCase(TestCase):
    def test_as_hosted_content(self):
        resources = [
            {
                'url': 'http://fake.com/style.css',
                'hosted_url': 'http://hosted.com/styles/style.css'
            },
            {
                'url': 'http://fake.com/1.png',
                'hosted_url': 'http://hosted.com/images/1.png'
            },
            {
                'url': 'http://fake.com/2.png',
                'hosted_url': 'http://hosted.com/images/2.png'
            }
        ]
        content = '''
        <html>
            <head>
                <link href="{url_style}" rel="stylesheet" />
            </head>
            <body>
                <img src="{img_a}" />
                <img src="{img_b}" />
            </body>
        </html>
        '''

        original_html = content.format(
            url_style=resources[0]['url'],
            img_a=resources[1]['url'],
            img_b=resources[2]['url']
        )
        expected_hosted = content.format(
            url_style=resources[0]['hosted_url'],
            img_a=resources[1]['hosted_url'],
            img_b=resources[2]['hosted_url']
        )
        self.assertEqual(
            utils.as_hosted_content(bytes(original_html, 'utf-8'), resources),
            bytes(expected_hosted, 'utf-8')
        )

    def test_mediaurl(self):
        self.assertEqual(
            utils.mediaurl('style.css'),
            'http://localhost:4000/media/style.css'
        )
        self.assertEqual(
            utils.mediaurl('style.css?v=0.0'),
            'http://localhost:4000/media/style.css?v=0.0'
        )

