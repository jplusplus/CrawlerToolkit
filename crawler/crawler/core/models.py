# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import URLValidator
from crawler.constants import STATES, FEED_TYPES
from crawler.core import managers
import re

valid_url = URLValidator(schemes=['http','https'])

def valid_feed_url(value):
    valid_url(value)
    twitter_patt = re.compile('https://twitter.com/\w+$')
    is_xml_feed = value.endswith('.xml')
    is_twitter_account = twitter_patt.match(value)
    if not (is_twitter_account or is_xml_feed):
        raise ValidationError((
            '%s is not a valid feed URL. It must either be twitter account URL'
            '(ex: https://twitter.com/toutenrab) or an RSS feed address '
            '(ex: http://www.lemonde.fr/rss/une.xml)'
        ) % value)

class Feed(models.Model):
    objects = managers.FeedManager()
    name = models.CharField(max_length=120, blank=False, null=False)
    active = models.BooleanField(default=True)
    url = models.URLField(
        unique=True,
        validators=[valid_feed_url],
        blank=False,
        help_text='Enter a RSS feed url or a twitter account URL.'
    )
    last_time_crawled = models.DateTimeField(null=True)

class Article(models.Model):
    objects = managers.ArticleManager()
    created_at = models.DateTimeField(auto_now_add=True)
    crawled_at = models.DateTimeField(null=True)
    feed = models.ForeignKey('Feed')
    url = models.URLField(db_index=True, unique=True, blank=False)
    archiving_state = models.CharField(max_length=12,
            choices=STATES.ARCHIVE.list(),
            blank=True)

    crawling_state = models.CharField(max_length=10,
            choices=STATES.CRAWL.list(),
            default=STATES.CRAWL.PROGRAMMED)

    detected_preservation_tags = models.CharField(max_length=37,blank=True)

    @property
    def source(self):
        return self.feed.name

