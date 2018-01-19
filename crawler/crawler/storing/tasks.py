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

# Scrapers 
from .scrapers import HTMLScraper

logger = get_task_logger(__name__)

def scrape_article_resources(url):
    scraper = HTMLScraper(url)
    html_content = scraper.html_content()
    html_resources = scraper.static_resources()
    css_resources = scraper.css_resources()
    # logger.info("sraped article")
    return [ html_content, html_resources, css_resources ]

def crawl_article_resources(article):
    [ html_content, resources, css_resources ] = scrape_article_resources(
        article.url
    )
    resources = utils.save_resources(article, resources, css_resources)
    utils.save_resource(
        article,
        {
            'filename': 'index.html',
            'content': utils.as_hosted_content(
                html_content,
                resources
            )
        },
        use_tdir=False,
        uniq_fn=False
    )
    return resources

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

