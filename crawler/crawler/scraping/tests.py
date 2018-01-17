from django.test import TestCase
from crawler.scraping.scrapers import page_metas, xml as xmlscraper

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
