# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import URLValidator
from crawler.constants import STATES, FEED_TYPES
from crawler.core import managers, tasks_utils
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

@receiver(post_save, sender=Feed)
def trigger_feed_crawl(sender, instance, created=False, *args, **kwargs):
    if created:
        from crawler.core.tasks_utils import crawl_feed
        crawl_feed(instance)

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

class PreservationTag(models.Model):
    article = models.ForeignKey('Article', related_name='preservation_tags')
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    leaf_objects = managers.LeafManager()

    class Meta:
        abstract = False

    def save(self, *args, **kwargs):
        """
        Overrides the default save method from Django. If the method is called for
        a new model, its content type will be saved in the database as well. This way
        it is possible to later determine if the model is an instance of the
        class itself or some of its subclasses.
        """

        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        super(PreservationTag, self).save(*args, **kwargs)

    def as_leaf_class(self):
        """
        Checks if the object is an instance of a certain class or one of its subclasses.
        If the instance belongs to a subclass, it will be returned as an instance of
        that class.
        """
        content_type = self.content_type
        model_class = content_type.model_class()
        if (model_class == self.__class__):
            return self
        return model_class.objects.get(id=self.id)

class PriorityTag(PreservationTag):
    value = models.BooleanField()

    @property
    def should_preserve(self):
        return self.value

class ReleaseDateTag(PreservationTag):
    value = models.DateTimeField(null=True)

    @property
    def should_preserve(self):
        return self.value is not None

class NotFoundOnlyTag(PreservationTag):
    value = models.BooleanField()

    @property
    def should_preserve(self):
        return self.value
