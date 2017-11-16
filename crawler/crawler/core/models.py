# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urllib.parse import urlparse
import re

from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.db import models
from crawler import utils
from crawler.constants import STATES
from crawler.core import managers, receivers, validators, inherithance
from crawler.core.tag_models import *
from crawler.core.resource_models import *
from slugger import AutoSlugField

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
    slug = AutoSlugField(populate_from='name')

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

def slugify_article_url(url):
    url = urlparse(url)
    path = url.path
    extension_pattern = re.compile('\.[\w]+$')
    if extension_pattern.match(path):
        path = path.split('.')[-1]
    path = '-'.join(
        list(filter(lambda _:len(_),path.split('/')))
    )
    return path

class Article(models.Model):
    objects = managers.ArticleManager()
    created_at = models.DateTimeField(auto_now_add=True)
    crawled_at = models.DateTimeField(null=True)
    title = models.CharField(max_length=200, default='Detecting title',
            null=False, blank=False)
    feed = models.ForeignKey('Feed')
    slug = AutoSlugField(
        populate_from='url',
        slugify=slugify_article_url
    )

    url = models.URLField(db_index=True, unique=True, blank=False)
    preservation_state = models.CharField(max_length=11,
            choices=STATES.PRESERVATION.list(),
            blank=True)

    archiving_state = models.CharField(max_length=12,
            choices=STATES.ARCHIVE.list(),
            blank=True,
            null=True)

    def html_content(self):
        return HTMLResource.objects.get(article_id=self.pk)

    def has_html_content(self):
        return HTMLResource.objects.filter(article_id=self.pk).count() > 0;

    @property
    def serve_url(self):
        kwargs = {
            'feed_slug': self.feed.slug,
            'article_slug': self.slug,
        }
        path = reverse('store:serve_article', kwargs=kwargs)
        return utils.absurl(path)
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

receivers.init()
