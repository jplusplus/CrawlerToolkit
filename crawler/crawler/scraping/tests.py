from django.test import TestCase
from django.utils import timezone
import requests_mock

from crawler.core.models import Feed, Article
from crawler.scraping import utils
from crawler.scraping import models
from crawler.scraping.models import PriorityTag,ReleaseDateTag,NotFoundOnlyTag
from crawler.scraping.scrapers import page_metas, xml as xmlscraper

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
        self.feed = Feed.objects.create(
            name='fake',
            url='http://fake.com/feed.xml'
        )
        self.article = Article.objects.create(
            feed=self.feed,
            url=self.fake_url
        )

    def checkMetas(self, _):
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

    def test_preservation_tag_type(self):
        self.assertEqual(
            models.preservation_tag_type(PriorityTag), 'preservation:priority'
        )
        self.assertEqual(
            models.preservation_tag_type(ReleaseDateTag), 'preservation:release_date'
        )
        self.assertEqual(
            models.preservation_tag_type(NotFoundOnlyTag), 'preservation:notfound_only'
        )

        with self.assertRaises(ValueError):
            models.preservation_tag_type(Feed)

    def test_preservation_tag_model(self):
        self.assertEqual(
            models.preservation_tag_model('preservation:priority'), PriorityTag
        )
        self.assertEqual(
            models.preservation_tag_model('preservation:release_date'), ReleaseDateTag
        )
        self.assertEqual(
            models.preservation_tag_model('preservation:notfound_only'),NotFoundOnlyTag
        )

        with self.assertRaises(ValueError):
            models.preservation_tag_model('preservation:not_existing')

    def test_save_tags(self):
        art = self.article
        [ title, tags ] = page_metas.parse(self.fake_html)
        tags = map(lambda _: [ art.pk, _ ], tags)
        saved_tags = utils.save_preservation_tags(tags)
        self.assertEqual(len(saved_tags), 3)

        priority = saved_tags[0]
        release_date = saved_tags[1]
        notfound_only = saved_tags[2]

        self.assertIsInstance(priority, PriorityTag)
        self.assertTrue(priority.value)

        self.assertIsInstance(release_date, ReleaseDateTag)
        self.assertEqual(
            release_date.value,
            timezone.datetime(
                2018, 1, 8, tzinfo=timezone.get_current_timezone()
            )
        )

        self.assertIsInstance(notfound_only, NotFoundOnlyTag)
        self.assertFalse(notfound_only.value)


class XMLFeedTestCase(TestCase):
    def setUp(self):
        self.feed_url = 'http://fake.com/feed.xml'
        self.link_a = 'http://fake.com/posts/1'
        self.link_b = 'http://fake.com/posts/2'

    def check_if_links_are_presents(self, links):
        return self.link_a in links and self.link_b in links

    def runTestWith(self, m, xml):
        xml = xml.format(link_a=self.link_a, link_b=self.link_b)
        m.register_uri('GET', self.feed_url, text=xml)
        links = xmlscraper.scrape(self.feed_url)
        self.assertIn(self.link_a, links)
        self.assertIn(self.link_b, links)

    @requests_mock.Mocker()
    def test_xml_rss(self, m):
        self.runTestWith(m, '''<?xml version="1.0" encoding="utf-8"?>
            <rss version="2.0">
                <channel>
                    <title>Fake</title>
                    <link>https://fake.com</link>
                    <item>
                        <link>{link_a}</link>
                    </item>
                    <item>
                        <link>{link_b}</link>
                    </item>
                </channel>
            </rss>
            '''
        )

    @requests_mock.Mocker()
    def test_xml_atom(self, m):
        self.runTestWith(m, '''<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>Fil d'exemple</title>
            <subtitle>Un titre secondaire.</subtitle>
            <link href="http://example.org/"/>
            <updated>2010-05-13T18:30:02Z</updated>
            <author>
                 <name>Paul Martin</name>
                 <email>paulmartin@example.com</email>
             </author>
             <id>urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6</id>
             <entry>
               <link href="{link_a}"/>
             </entry>
             <entry>
               <link href="{link_b}"/>
             </entry>
        </feed>
        ''')
