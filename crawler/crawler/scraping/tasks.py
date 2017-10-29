from datetime import datetime
import re
from celery.utils.log import get_task_logger
from celery.decorators import task
from crawler.constants import FEED_TYPES
from crawler.celery import app
# Scrapers 

from .scrapers import twitter, rss, page_metas

logger = get_task_logger(__name__)

is_twitter_feed = lambda url: url.startswith('https://twitter.com/')
is_xml_feed = lambda url: url.endswith('\.xml')

@task
def crawl_feeds():
    from crawler.core.tasks_utils import active_feeds, save_feeds_urls
    feeds = active_feeds()
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
    """
    all_urls = list()
    for feed in feeds:
        feed_url = feed.url
        detected_urls = list()
        if is_twitter_feed(feed_url):
            detected_urls = twitter.scrape(feed_url)

        elif is_xml_feed(feed_url):
            detected_urls = rss.scrape(feed_url)
        else:
            raise ValueError((
                'Feed located at %s wasn\'t recognised, please inform your'
                'administrator'
            ) % feed_url )

        detected_urls = list(map(lambda url:[feed.pk, url], detected_urls))
        all_urls = all_urls + detected_urls
        save_feeds_urls(all_urls)
        feed.last_time_crawled = datetime.now()
        feed.save()

    return { 'success': True }


@task
def crawl_page_metas(url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    return page_metas.scrape(url)
