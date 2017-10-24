# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from .constants import STATES


class Feed(models.Model):
    last_crawled = models.DateField()

class TwitterFeed(Feed):
    account_name = models.CharField(max_length=15, blank=False)

class RSSFeed(Feed):
    rss_url = models.URLField()

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

