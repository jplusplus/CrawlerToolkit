# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from crawler.constants import STATES, FEED_TYPES


class Feed(models.Model):
    last_time_crawled = models.DateTimeField()
    def url(self):
        raise NotImplementedError(
            'All descendants of Feed model must implement the url method.'
        )

    def type(self):
        raise NotImplementedError(
            'All descendants of Feed model must implement the type method.'
        )

class TwitterFeed(Feed):
    account_name = models.CharField(max_length=15, blank=False)

    def url(self): return self.account_name
    def type(self): return FEED_TYPES.TWITTER

class RSSFeed(Feed):
    rss_url = models.URLField()
    def url(self): return self.rss_url
    def type(self): return FEED_TYPES.RSS

class Article(models.Model):
    feed = models.ForeignKey('Feed')
    article_url = models.URLField()
    archiving_state = models.CharField(max_length=12,
            choices=STATES.ARCHIVE.list(),
            blank=True)

    crawling_state = models.CharField(max_length=10,
            choices=STATES.CRAWL.list(),
            default=STATES.CRAWL.PROGRAMMED)

    detected_preservation_tags = models.CharField(max_length=37,blank=True)

