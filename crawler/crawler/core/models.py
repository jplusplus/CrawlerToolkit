# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Feed(models.Model):
    last_crawled = models.DateField

ARTICLE_CRAWLING_STATE = (
    ('CRAWLED', 'Crawled'),
    ('CRAWLING', 'Crawling'),
    ('CRAWLING_PROGRAMMED', 'Crawling programmed'),
)

ARTICLE_ARCHIVING_STATE = (
    ('ARCHIVED', 'Archived'), # Already archived (date given by archiving_date)
    ('ARCHIVING', 'Archiving'), # Will start soon or will start at start_archiving_date
    ('NO_ARCHIVING', 'No archiving needed'), # Article crawled but doesn't need archiving.
)

ARTICLE_DETECTED_PRESERVATION_TAGS = (
    ('PRIORITY', 'preservation:priority'),
    ('RELEASE_DATE', 'preservation:release_date'),
    ('NOT_FOUND_ONLY', 'preservation:notfound_only'), 
)

class Article(models.Model):
    archiving_state = models.CharField(max_length=12)

# Create your models here.
