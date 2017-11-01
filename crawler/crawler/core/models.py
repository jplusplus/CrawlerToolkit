# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.db import models
from crawler.constants import STATES
from crawler.core import managers, signals, validators, inherithance

from crawler.core.tag_models import *
from crawler.core.resource_models import *

class Feed(models.Model):
    objects = managers.FeedManager()
    name = models.CharField(max_length=120, blank=False, null=False)
    active = models.BooleanField(default=True)
    url = models.URLField(
        unique=True,
        validators=[validators.valid_feed_url],
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

    @property
    def source(self):
        return self.feed.name

    @property
    def should_preserve(self):
        return any(
            map(
                lambda tag: tag.should_preserve,
                self.preservation_tags.all()
            )
        )

signals.init()
