from datetime import datetime
from celery.utils.log import get_task_logger
from celery.decorators import task
from crawler.constants import FEED_TYPES
from crawler.celery import app
# Scrapers 

from .scrapers import twitter, rss, page_metas

logger = get_task_logger(__name__)


@task
def crawl_feeds():
    from crawler.core.models import Feed
    feeds = Feed.objects.active_feeds()
    logger.info('crawl_feeds called %s' % feeds)
    """
    Loops on the given feeds and decide which scraper to use (see
    `twitter_scrape` and `rss_scrape`).
    Parameters:
        - feeds, a list() of dict() formated like this:
            {
                id: '' # The PK of the feed.
                url: '' # the URL of the feed.
                type: '' # the feed's type (twitter, rss etc.)
            }
    Returns an array of the feeds with detected URLs.
    """
    for feed in feeds:
        detected_urls = list()
        if feed.type() is FEED_TYPES.TWITTER:
            detected_urls = twitter.scrape(feed.url())

        if feed.type() is FEED_TYPES.RSS:
            detected_urls = rss.scrape(feed.url())

        feed.last_time_crawled = datetime()
        feed.save()

    return { 'success': True }


@task
def crawl_page_metas(url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    return page_metas.scrape(url)
