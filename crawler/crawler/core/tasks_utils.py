from datetime import datetime
import re

from celery.utils.log import get_task_logger

from django.db import transaction
from django.core.files.base import ContentFile
from crawler.constants import PRESERVATION_TAGS, STATES
from crawler.utils import pickattr, mediaurl

logger = get_task_logger(__name__)

def qs_or_ids(qs, f):
    if not qs or len(qs) == 0: return qs
    if type(qs[0]) == type(0):
        qs  = f(qs)
    return qs

def filter_by_id(Model,ids):return Model.objects.filter(pk__in=ids)

def feeds(ids):
    from crawler.core.models import Feed
    return filter_by_id(Feed, ids)

def active_feeds():
    from crawler.core.models import Feed
    return Feed.objects.active_feeds()

def articles(ids):
    from crawler.core.models import Article
    return filter_by_id(Article, ids)
