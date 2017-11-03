from django.urls import reverse
from celery.decorators import task
from celery.contrib import rdb
from crawler import utils
from crawler.archiving.models import ArchivedArticle
from .scrapers import detect_notfound, archive

def notify_archived(articles):
    articles_archived.send(articles)

def archive_article(article):
    from crawler.constants import STATES
    article.archiving_state=STATES.ARCHIVE.ARCHIVING
    article.save()
    try:
        article_path = reverse('store:serve_article', kwargs={
            'feed_slug':article.feed.slug,
            'article_slug':article.slug
        })
        article_url = utils.absurl(article_path)
        for start_service in archive.services(article_url):
            archived_url = start_archive()
            ArchivedArticle.object.create(
                url=archived_url,
                article=article)

        article.archiving_state = STATES.ARCHIVE.ARCHIVED
    except Exception as e:
        article.archiving_state = None

    article.save()

@task(ignore_results=True)
def archive_articles(ids=None, qs=None):
    from crawler.core import tasks_utils
    articles = list()
    if not qs:
        articles = tasks_utils.articles(ids)
    else:
        articles = qs

    for article in articles:
        archive_article(article)

@task(ignore_results=True)
def check_articles_to_archive():
    from crawler.core import tasks_utils
    articles = list()
    articles = articles + tasks_utils.release_date_articles()
    articles = articles + detect_notfound(
        tasks_utils.notfound_only_articles()
    )
    articles = articles + tasks_utils.priority_articles()
    articles = articles + tasks_utils.release_date_articles()
    archive_articles(tasks_utils.pickattr(articles, 'pk'))

