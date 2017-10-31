from datetime import datetime
import re
from celery.utils.log import get_task_logger
from celery.decorators import task
from crawler.constants import FEED_TYPES
from crawler.celery import app
# Scrapers 

from .scrapers import twitter, xml, page_metas

logger = get_task_logger(__name__)

is_twitter_feed = lambda url: url.startswith('https://twitter.com/')
is_xml_feed = lambda url: url.endswith('.xml')

@task
def crawl_feed(feed_id, feed_url):
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

@task
def crawl_feeds(feeds):
    all_urls = list()
    for feed in feeds:
        all_urls = all_urls + crawl_feed(feed.pk, feed.url)
        feed.last_time_crawled = datetime.now()
        feed.save()
    return all_urls

@task
def crawl_active_feeds():
    from crawler.core.tasks_utils import active_feeds, save_feeds_urls
    all_urls = crawl_feeds(active_feeds())
    articles = save_feeds_urls(all_urls)
    preservation_tags = crawl_articles_preservation_tags(articles)
    save_articles_preservation_tags(preservation_tags)

@task
def crawl_article_preservation_tags(article_id, article_url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    metas = page_metas.scrape(article_url)
    return list(map(lambda meta: [article_id, meta], metas))

@task
def crawl_articles_preservation_tags(articles, *args, **kwargs):
    tags = list()
    for article in articles:
        article_tags = crawl_article_preservation_tags(article.pk, article.url)
        tags = tags + article_tags
    return tags
