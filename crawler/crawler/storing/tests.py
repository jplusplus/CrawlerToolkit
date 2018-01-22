from django.conf import settings

from django.test import TestCase
from crawler.core.models import Feed, Article
from crawler.storing import scrapers, utils
from crawler.constants import RESOURCE_TYPES

import requests_mock

class StoringTestCase(TestCase):
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
        self.feed = Feed.objects.create(name='fake', url='http://fake.com')
        self.article = Article.objects.create(
            feed=self.feed, url=self.url
        )

    def mockServer(self, m):
        m.register_uri('GET', self.img_url, text=self.img)
        m.register_uri('GET', self.url, text=self.html)
        m.register_uri('GET', self.style_url, text=self.css)
        return m

class ScrapersTestCase(StoringTestCase):
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
        content = scraper.content()
        html = content['content']
        resources = content['resources']
        self.assertEqual(
            html.decode('utf-8'),
            self.html
        )
        self.assertEqual(
            len(resources[RESOURCE_TYPES.STYLE]),
            1
        )

        self.assertEqual(
            len(resources[RESOURCE_TYPES.IMAGE]),
            1
        )

class UtilsTestCase(StoringTestCase):
    @requests_mock.Mocker()
    def test_save_article_resources(self, m):
        self.mockServer(m)
        scraper = scrapers.HTMLScraper(self.article.url)
        utils.save_article_resources(self.article, scraper)
        self.assertTrue(self.article.has_index_resource())

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
        domain = settings.DOMAIN_NAME
        media = settings.MEDIA_URL
        self.assertEqual(
            utils.mediaurl('style.css'),
            'http://localhost:4000/media/style.css'.format(domain, media)
        )
        self.assertEqual(
            utils.mediaurl('style.css?v=0.0'),
            '{0}{1}style.css?v=0.0'.format(domain, media)
        )

        with self.settings(
            MEDIA_URL='https://fake-aws.s3.amazonaws.com/archive/'
        ):
            self.assertEqual(
                utils.mediaurl('style.css'),
                'https://fake-aws.s3.amazonaws.com/archive/style.css'
            )
    def test_article_mediaurl(self):
        resource_path = self.article.resource_path(
            filename='style.css',
            resource_type=RESOURCE_TYPES.STYLE,
            uniq_fn=False)

        with self.settings(
            MEDIA_URL='https://fake-aws.s3.amazonaws.com/archive/'
        ):
            self.assertEqual(
               utils.mediaurl(resource_path),
               'https://fake-aws.s3.amazonaws.com/archive/fake/my-post/stylesheets/style.css'
            )

