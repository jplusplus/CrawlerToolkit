# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import URLValidator
from crawler.constants import STATES, FEED_TYPES
from crawler.core import managers
from polymorphic.models import PolymorphicModel
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
    active = models.BooleanField(default=True)
    url = models.URLField(
        validators=[valid_feed_url],
        blank=False,
        help_text='Enter a RSS feed url or a twitter account URL.'
    )
    last_time_crawled = models.DateTimeField(null=True)

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

