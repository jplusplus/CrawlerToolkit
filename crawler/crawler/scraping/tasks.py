from datetime import datetime
from celery.decorators import task

from crawler.constants import FEED_TYPES
# Scrapers 
from .page import page_scrape
from .rss import rss_scrape
from .twitter import twitter_scrape

@task(name='crawl_feeds')
def crawl_feeds(feeds,*args, **kwargs):
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
        if feed.type is FEED_TYPES.TWITTER:
            detected_urls = twitter_scrape(feed.url)

        if feed.type is FEED_TYPES.RSS:
            detected_urls = rss_scrape(feed.url)

        feed['detected_urls'] = detected_urls
        feed['last_time_crawled'] = datetime()

   return feeds


@task(name='crawl_page_metas')
def crawl_page_metas(url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    return page_meta_scraper(url)
