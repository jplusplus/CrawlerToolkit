# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.utils import timezone
from django.test import TestCase

from crawler.constants import STATES
from crawler.core import validators, models
from crawler.scraping.models import PriorityTag, ReleaseDateTag, NotFoundOnlyTag

class CoreTestCase(TestCase):
    def setUp(self):
        from crawler.celery import app
        self.celery = app

    def test_celery(self):
        print('\ntasks: %s\n' % self.celery.tasks)
        self.assertIsNotNone(self.celery)

Feed = models.Feed
Article = models.Article

class FeedsTestCase(TestCase):
    def setUp(self):
        self.inactive_feed = Feed.objects.create(
            name='Toutenrab account',
            url='https://twitter.com/toutenrab',
            active=False
        )
        self.active_feed = Feed.objects.create(
            name='NKB account',
            url='https://twitter.com/nkb',
            active=True
        )

        Article.objects.create(url='http://fakeurl.com/1/', feed=self.active_feed)

    def test_active_feeds(self):
        active_feeds = Feed.objects.active()
        self.assertEqual(active_feeds.count(), 1)
        self.assertEqual(active_feeds.first().url, self.active_feed.url)

    def test_save_urls(self):
        """
        Test if we can create new articles
        It should create only non-existing URLs
        """
        urls = [
            (self.active_feed.pk, 'http://fakeurl.com/1/'),
            (self.active_feed.pk, 'http://fakeurl.com/2/'),
            (self.active_feed.pk, 'http://fakeurl.com/2/'),
            (self.active_feed.pk, 'http://fakeurl.com/3/'),
        ]
        saved_urls = Article.objects.save_urls(urls)
        self.assertEqual(len(saved_urls), 2)
        self.assertTrue(isinstance(saved_urls, QuerySet))

class AssertAllMixin(object):
    def assertAll(self, function, iterable):
        self.assertTrue(all(map(function, iterable)))

class ArticleTestCase(TestCase, AssertAllMixin):
    def createFeeds(self):
        self.feed = Feed.objects.create(
            name='toutenrab',
            url='http://twitter.com/toutenrab',
            active=True
        )

    def createTags(self):
        PriorityTag.objects.create(
            value=False,
            article=self.first_art
        )
        ReleaseDateTag.objects.create(
            value=timezone.now(),
            article=self.first_art
        )

    def createArticles(self):
        self.first_art = Article.objects.get_or_create(
            url='http://fakeurl.com/1/',
            feed=self.feed
        )[0]
        self.second_art = Article.objects.get_or_create(
            url='http://fakeurl.com/2/',
            feed=self.feed
        )[0]

    def setUp(self):
        self.createFeeds()
        self.createArticles()
        self.createTags()

    def test_slug(self):
        self.assertEqual(self.first_art.slug, '1')

    def test_slugify_article_url(self):
        url = 'http://fakeurl.com/a/fake/url/example.html'
        slug = models.slugify_article_url(url)
        self.assertEqual(slug, 'a-fake-url-example')

    def test_resources_dir(self):
        self.assertEqual(self.first_art.resources_dir(), 'toutenrab/1')

    def test_preservation_tags(self):
        tags = self.first_art.preservation_tags()
        self.assertTrue(isinstance(tags, QuerySet))
        self.assertEqual(tags.count(), 2)

    def test_set_preserving(self):
        is_preserving = lambda el: el.preservation_state == STATES.PRESERVATION.PRESERVING
        articles = Article.objects.all()
        articles.set_preserving()
        self.assertAll(is_preserving, articles)

    def test_set_archiving(self):
        is_archiving = lambda el: el.archiving_state == STATES.ARCHIVE.ARCHIVING
        articles = Article.objects.all()
        articles.set_archiving()
        self.assertAll(is_archiving, articles)

    def test_set_crawled(self):
        articles = Article.objects.all()
        articles.set_crawled()
        a = Article.objects.get(pk=self.first_art.pk)
        b = Article.objects.get(pk=self.second_art.pk)
        self.assertEqual(a.preservation_state, STATES.PRESERVATION.PRESERVE)
        self.assertEqual(b.preservation_state, STATES.PRESERVATION.NO_PRESERVE)

class ValidatorsTestCase(TestCase):
    def assertError(self, url, should_have_raised=True):
        error_raised = False
        try:
            validators.valid_feed_url(url)
        except ValidationError:
            error_raised = True

        self.assertEqual(error_raised, should_have_raised)

    def test_valid_feed_url(self):
        self.assertError('https://twitter.com/toutenrab', False)
        self.assertError('http://lemonde.fr/rss/une.xml', False)

    def test_invalid_feed_url(self):
        self.assertError('https://twitter.com/')
        self.assertError('https://fake.com/')

