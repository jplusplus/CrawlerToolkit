from django.test import TestCase
from django.db import models
from django.conf import settings

from crawler import utils
from crawler.core.models import Feed, Article

class UtilsTestCase(TestCase):
    def setUp(self):
        feed = Feed.objects.create(
            name='fake feed',
            url='http://fake-url.com/feed.xml'
        )
        self.feed = feed
        self.article_a = Article.objects.create(
            feed=feed,
            url='http://fake-url.com/article/a'
        )
        self.article_b = Article.objects.create(
            feed=feed,
            url='http://fake-url.com/article/b'
        )

    def test_POPO(self):
        popo = utils.POPO()
        popo.a = 'test'
        self.assertEqual(popo.a, 'test')\

    def test_absurl(self):
        self.assertEqual(
            utils.absurl('fake/path'),
            settings.DOMAIN_NAME + 'fake/path'
        )

    def test_pickattr(self):
        urls = utils.pickattr(
            Article.objects.filter(feed=self.feed),
            'url'
        )
        self.assertEqual(len(urls), 2)
        self.assertTrue(self.article_a.url in urls)
        self.assertTrue(self.article_b.url in urls)

    def test_strtobool(self):
        self.assertEqual(utils.strtobool('  true '), True)
        self.assertEqual(utils.strtobool('true'), True)
        self.assertEqual(utils.strtobool('True'), True)
        self.assertEqual(utils.strtobool('TRUE'), True)

        self.assertEqual(utils.strtobool(''), False)
        self.assertEqual(utils.strtobool('false'), False)
        self.assertEqual(utils.strtobool('tru'), False)

    def test_modelcounts(self):
        counts = list(utils.modelcounts())
        for count in counts:
            self.assertTrue(issubclass(count[0], models.Model))
            self.assertIsInstance(count[1], int)


        counts_a = list(utils.modelcounts(sort=True))
        counts_b = list(utils.modelcounts(
            sort=True, reverse=False
        ))

        self.assertTrue(counts_a[0][1] > counts_a[-1][1])
        self.assertTrue(counts_b[0][1] < counts_b[-1][1])

