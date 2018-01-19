from datetime import datetime
import re
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery.contrib import rdb
from django.core.files.storage import default_storage as storage

from celery.decorators import task
from crawler.celery import app
from crawler.constants import STATES, RESOURCE_TYPES
from crawler.storing import utils
from crawler.storing.scrapers import HTMLScraper

logger = get_task_logger(__name__)

def crawl_article_resources(article):
    scraper = HTMLScraper(article.url)
    return utils.save_article_resources(article, scraper)

@task
def crawl_resources(ids):
    from crawler.core.models import Article
    logger.debug('crawl_resources(%s)' % ids)
    articles = Article.objects.ids(ids).should_be_preserved().is_not_stored()
    articles.set_preserving()
    resources = map(crawl_article_resources, articles)
    logger.debug('\ncrawled resources: \n\t%s\n\n' % list(resources))
    articles.set_stored()
    return ids

