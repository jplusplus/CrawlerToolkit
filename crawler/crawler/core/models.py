# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from urllib.parse import urlparse

from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.core.files.storage import default_storage as storage
from django.db import models
from django.urls import reverse
from django.utils import timezone

from slugger import AutoSlugField

from crawler import utils
from crawler.constants import STATES
from crawler.core import managers, receivers, validators
from crawler.scraping.models import PriorityTag, NotFoundOnlyTag, ReleaseDateTag

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

    if re.match('.*\.[\w]+$', path):
        path = '.'.join(path.split('.')[:-1])

    path = '-'.join(
        list(filter(lambda _: len(_), path.split('/')))
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

    def preservation_tags(self):
        qs = NotFoundOnlyTag.objects.filter(article=self)
        qs = qs.union(
            ReleaseDateTag.objects.filter(article=self)
        ).union(
            PriorityTag.objects.filter(article=self)
        )
        return qs

    def resources_dir(self):
        return '/'.join([ self.feed.slug, self.slug ])

    def resource_path(self, fn, resource_type=None, use_tdir=True, uniq_fn=True):
        resources_dir = self.resources_dir()
        if use_tdir:
            if resource_type != None:
                resources_dir += '/{}s'.format(resource_type)
            else:
                raise Error("Must set resource_type argument")
        if uniq_fn:
            ext = filename.split('.')[-1]
            fid = str(uuid4())
            filename = "{}.{}".format(fid, ext)

        return "{path}/{fn}".format(path=resources_dir, fn=fn)

    def index_path(self):
        return self.resource_path('index.html', use_tdir=False, uniq_fn=False)

    def index_resource(self):
        return storage.open(self.index_path(), 'r')

    def has_index_resource(self):
        return storage.exists(self.index_path())

    def deletedir(self):
        return storage.deletedir(self.resources_dir())

    def set_crawled(self):
        self.crawled_at = timezone.now()
        if not self.should_preserve:
            self.preservation_state = STATES.PRESERVATION.NO_PRESERVE
        elif self.preservation_state != STATES.PRESERVATION.STORED:
            self.preservation_state = STATES.PRESERVATION.PRESERVE
        return self

    def set_stored(self):
        self.preservation_state = STATES.PRESERVATION.STORED

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
        prio = PriorityTag.objects.filter(article=self, value=True)
        if prio.count() > 0:
            return False
        rdtag = ReleaseDateTag.objects.filter(
            article=self,
            value__lte=timezone.now()
        )
        nftag = NotFoundOnlyTag.objects.filter(
            article=self,
            value=True
        )
        return rdtag.exists() or nftag.exists()

receivers.init()
