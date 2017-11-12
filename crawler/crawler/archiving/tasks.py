from django.urls import reverse
from celery.decorators import task
from celery.utils import log
from crawler import utils
from crawler.archiving.models import ArchivedArticle
from .scrapers import detect_notfound, archive

logger = log.get_task_logger(__name__)

def notify_archived(articles):
    articles_archived.send(articles)

def archive_article(article):
    from crawler.constants import STATES
    article.archiving_state=STATES.ARCHIVE.ARCHIVING
    article.save()
    service_name = ''
    archived_url = ''
    try:
        article_path = reverse('store:serve_article', kwargs={
            'feed_slug':article.feed.slug,
            'article_slug':article.slug
        })
        article_url = utils.absurl(article_path)
        for service in archive.services(article_url):
            service_name = service.name()
            prev_archive = ArchivedArticle.objects.filter(
                service=service_name,
                article=article
            )
            if not prev_archive.exists():
                archived_url = service.start()
                ArchivedArticle.objects.create(
                    service=service_name,
                    url=archived_url,
                    article=article)

        article.archiving_state = STATES.ARCHIVE.ARCHIVED
    except Exception as e:
        article.archiving_state = STATES.ARCHIVE.ERROR
        logger.error("An error occured when archiving article", e)
        logger.info("Article path: %s" % article_path)
        logger.info("Article absolute url: %s" % article_url)
        logger.info("Archived url (%s): %s" %  (service_name, archived_url))

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
    notfound_articles = detect_notfound(
        tasks_utils.notfound_only_articles()
    )
    # logger.info('Detected %s not found articles' % len(notfound_articles))
    priority_articles = tasks_utils.priority_articles()
    release_date_articles =  tasks_utils.release_date_articles()

    articles = notfound_articles + priority_articles + release_date_articles
    archive_articles(list(set(tasks_utils.pickattr(articles, 'pk'))))

