from datetime import datetime
import re
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery.contrib import rdb

from celery.decorators import task
from crawler.constants import FEED_TYPES
from crawler.celery import app

# Scrapers 
from .scrapers import twitter, xml, page_metas
from .scrapers.html import HTMLScraper

logger = get_task_logger(__name__)

is_twitter_feed = lambda url: url.startswith('https://twitter.com/')
is_xml_feed = lambda url: url.endswith('.xml')

def __crawl_feed(feed_id, feed_url):
    detected_urls = list()
    if is_twitter_feed(feed_url):
        detected_urls = twitter.scrape(feed_url)
    elif is_xml_feed(feed_url):
        detected_urls = xml.scrape(feed_url)
    else:
        raise ValueError((
            'Feed located at %s wasn\'t recognised, please inform your '
            'administrator'
        ) % feed_url )
    return list(map(lambda url:[feed_id, url], detected_urls))

def __feeds_urls(feeds):
    all_urls = list()
    for feed in feeds:
        all_urls = all_urls + __crawl_feed(feed.pk, feed.url)
    return all_urls

@task(ignore_results=True)
def crawl_articles(ids=None, qs=None):
    from crawler.core import tasks_utils as utils
    from crawler.archiving.tasks import archive_articles
    if ids and not qs:
        articles = utils.articles(ids)
    else:
        articles = qs
    # we delete previously detected of the given articles
    utils.delete_tags_of(articles)
    # we crawl (and create) the apprioriate preservation tags
    crawl_preservation_tags(articles)
    # now that our articles are tagged we can crawl & store the resources
    # of the articles that must be stored
    crawl_resources(utils.should_be_preserved(articles))
    # Now that resources have been crawled we can stored
    archive_articles.delay(
        utils.pickattr(utils.should_be_archived(articles), 'pk')
    )

@task(ignore_results=True)
def crawl_feeds(feed_ids=None):
    """This task must be called with a list of feed ids.
    If none is given then it will lookup for active feeds (see
    `tasks_utils.active_feeds`). It will behave as following:
        for every feed given get latest links. If needed create
        the needed links. For every created article (link), look
        for preservation_tags.
    """
    from crawler.core import tasks_utils as utils
    qs = None
    if not feed_ids:
        qs = utils.active_feeds()
    else:
        qs = utils.feeds(feed_ids)

    articles_urls = __feeds_urls(qs)
    qs.update(last_time_crawled=timezone.now())
    articles = utils.create_articles(articles_urls)
    # crawl created articles
    crawl_articles(qs=articles)

def article_preservation_tags(article_id, article_url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    metas = page_metas.scrape(article_url)
    return list(map(lambda meta: [article_id, meta], metas))

def crawl_preservation_tags(articles, *args, **kwargs):
    from crawler.core.tasks_utils import set_articles_crawled, save_preservation_tags
    tags = list()
    for article in articles:
        article_tags = article_preservation_tags(article.pk, article.url)
        tags = tags + article_tags
    tags = save_preservation_tags(tags)
    set_articles_crawled(articles)
    return tags


def scrape_article_resources(url):
    scraper = HTMLScraper(url)
    html_content = scraper.html_content()
    html_resources = scraper.static_resources()
    css_resources = scraper.css_resources()
    logger.info("sraped article")
    return [ html_content, html_resources, css_resources ]

def crawl_article_resources(article):
    from crawler.core import tasks_utils as utils
    [ html_content, resources, css_resources ] = scrape_article_resources(article.url)
    utils.save_resources(article, html_content, resources, css_resources)

@task
def crawl_resources(articles):
    for article in articles:
        crawl_article_resources(article)

