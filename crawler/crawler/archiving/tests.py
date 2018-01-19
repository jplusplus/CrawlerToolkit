from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
import random
import requests
import requests_mock

from crawler.utils import pickattr, slimmer
from crawler.core.models import Feed, Article
from crawler.storing import utils as storing
from crawler.archiving.services import ArchiveORG, Service
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

    def test_archive_org(self):
        archive = ArchiveORG('http://google.fr')
        self.assertEqual(archive.name(), 'ArchiveORG')
        archived_url = archive.start()
        self.assertIsNotNone(archived_url)

fake_html = '''<html>
    <body><h1>Test</h1></body>
</html>'''

class ViewsTestCase(TestCase):
    def setUp(self):
        self.html = fake_html
        self.feed = Feed.objects.create(name='fake', url='http://fake.com')
        self.article_to_archive = Article.objects.create(feed=self.feed,
                url='http://fake.com/posts/should-archive/')

        storing.save_html(
            self.article_to_archive,
            self.html,
            []
        )
        self.article_without_resource = Article.objects.create(feed=self.feed,
                url='http://fake.com/posts/should-not-archive/')
        self.password = 'fakepass'
        self.user = User.objects.create_user('fake', 'fake@fake.com', self.password)

    def test_article_preview_authenticated(self):
        article = self.article_to_archive
        c = Client()
        logged = c.login(username=self.user.username, password=self.password)
        self.assertTrue(logged)
        req = c.get(reverse('store:preview_article', kwargs={
            'feed_slug': article.feed.slug,
            'article_slug': article.slug
        }))
        content = list(req.streaming_content)[0].decode("utf-8")
        self.assertEqual(
            slimmer.html_slimmer(self.html),
            slimmer.html_slimmer(content)
        )
        self.assertEqual(req.status_code, 200)

    def test_article_preview_unauthenticated(self):
        article = self.article_to_archive
        c = Client()
        req = c.get(reverse('store:preview_article', kwargs={
            'feed_slug': article.feed.slug,
            'article_slug': article.slug
        }), follow=False)
        self.assertEqual(req.status_code, 302)

    def test_article_serve_not_archiving(self):
        article = self.article_to_archive
        c = Client()
        req = c.get(reverse('store:serve_article', kwargs={
            'feed_slug': article.feed.slug,
            'article_slug': article.slug
        }), follow=False)
        self.assertEqual(req.status_code, 403)

    def test_article_serve_archiving(self):
        article = self.article_to_archive
        Article.objects.filter(pk=article.pk).set_archiving()
        c = Client()
        req = c.get(reverse('store:serve_article', kwargs={
            'feed_slug': article.feed.slug,
            'article_slug': article.slug
        }))
        content = list(req.streaming_content)[0].decode("utf-8")
        self.assertEqual(
            slimmer.html_slimmer(self.html),
            slimmer.html_slimmer(content)
        )
        self.assertEqual(req.status_code, 200)

    def test_article_serve_without_html(self):
        article = self.article_without_resource
        Article.objects.filter(pk=article.pk).set_archiving()
        c = Client()
        req = c.get(reverse('store:serve_article', kwargs={
            'feed_slug': article.feed.slug,
            'article_slug': article.slug
        }))
        self.assertEqual(req.status_code, 404)
