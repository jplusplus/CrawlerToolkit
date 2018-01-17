from django.test import TestCase
import random
import requests_mock

from crawler.utils import pickattr
from crawler.core.models import Feed, Article
from crawler.archiving.scrapers import detect_notfound

class ScrapersTestCase(TestCase):
    def setUp(self):
        self.feed = Feed.objects.create(
            name='fake', url='http://fake-url.com/feed.xml'
        )

    def mockArticles(self, m, nb=500):
        articles = list()
        r = range(0, nb)
        for i in r:
            n = random.randint(0, 50)
            status = 200 if n % 2 == 0 else 404
            url = 'http://fake-url.com/%s/' % i
            article = Article.objects.create(
                feed=self.feed,
                url=url
            )
            articles.append((article, status))
            m.register_uri('GET', url, status_code=status, text='article %s' % i)
        return articles

    @requests_mock.Mocker()
    def test_detect_notfound(self, m):
        articles = self.mockArticles(m, 200)
        qs = Article.objects.ids(pickattr(map(lambda _: _[0], articles), 'pk'))
        expected_not_found = map(
            lambda _: _[0],
            filter(lambda _: _[1] == 404, articles)
        )

        not_found_articles = detect_notfound(qs)

        self.assertTrue(all(
            map(lambda a: a in expected_not_found, not_found_articles)
        ))

