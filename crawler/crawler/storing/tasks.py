from celery.utils.log import get_task_logger
# from celery.contrib import rdb

from celery.decorators import task
from crawler.storing import utils
from crawler.storing.scrapers import HTMLScraper

logger = get_task_logger(__name__)

def crawl_article_resources(article):
    scraper = HTMLScraper(article.url)
    return utils.save_article_resources(article, scraper)

@task
def crawl_resources(ids):
    from crawler.core.models import Article
    articles = Article.objects.ids(ids).should_be_preserved().is_not_stored()
    articles.set_preserving()
    for a in articles:
        crawl_article_resources(a)

    articles.set_stored()
    return ids

