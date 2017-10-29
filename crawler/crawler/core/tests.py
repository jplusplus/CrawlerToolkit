# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from crawler.core.models import Feed, Article
from crawler.core.tasks_utils import active_feeds, save_feeds_urls

# Create your tests here.

class FeedsTestCase(TestCase):
    def setUp(self):
        self.inactive_feed = Feed.objects.create(url='https://twitter.com/toutenrab', active=False)
        self.active_feed = Feed.objects.create(url='https://twitter.com/nkb', active=True)

        Article.objects.create(url='http://fakeurl.com/1/', feed=self.active_feed)

    def test_active_feeds(self):
        _active_feeds = active_feeds()
        self.assertEqual(_active_feeds.count(), 1)
        self.assertEqual(_active_feeds.first().url, self.active_feed.url)

    def test_save_feeds_urls(self):
        urls = [
            (self.active_feed.pk, 'http://fakeurl.com/1/'),
            (self.active_feed.pk, 'http://fakeurl.com/2/'),
            (self.active_feed.pk, 'http://fakeurl.com/2/'),
            (self.active_feed.pk, 'http://fakeurl.com/3/'),
        ]
        saved_urls = save_feeds_urls(urls)
        self.assertEqual(len(saved_urls), 2)
