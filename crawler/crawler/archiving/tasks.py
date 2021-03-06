from django.urls import reverse

from celery.decorators import task
from celery.utils import log

from crawler import utils
from crawler.archiving import services as archive
from crawler.archiving.scrapers import detect_notfound
from crawler.archiving.models import ArchivedArticle

from crawler.constants import STATES

logger = log.get_task_logger(__name__)

def archive_article(article):
    service_name = ''
    archived_url = ''
    # First case: we have no preservation, thus in case of
    # preservation:priority meta tag.
    article_url = article.url

    # Second case: every article that has preservation needs thus other meta
    # tags
    if article.preservation_state != STATES.PRESERVATION.NO_PRESERVE:
        article_path = reverse('store:serve_article', kwargs={
            'feed_slug':article.feed.slug,
            'article_slug':article.slug
        })
        article_url = utils.absurl(article_path)

    try:
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
        article.save()
    except Exception as e:
        article.archiving_state = STATES.ARCHIVE.ERROR
        article.save()
        raise e

@task(ignore_results=True)
def archive_articles(ids=None, skip_filter=False):
    """
    Archive the given articles by id. If not set, it will filter the articles
    by archive status (based on preservation tags information, see
    `core.managers.ArticleManager`.

    Params:
        - ids, list of articles ids
    """
    from crawler.core.models import Article
    articles = Article.objects.ids(ids)
    if not skip_filter:
        articles = articles.should_be_archived()

    articles.set_archiving()
    for article in articles:
        try:
            archive_article(article)
        except Exception as e:
            logger.error('An error occured while archiving article', e)

    return True

@task(ignore_results=True)
def check_articles_to_archive():
    """
    Task to detect if some articles are needing archiving (when 404, when
    release date is passed or when tagged with priority=true).

    """
    from crawler.core.models import Article
    # Filter articles that can't be archived
    articles = Article.objects.all().should_be_archived()
    articles = articles.should_be_archived()
    # queryset of articles needing immediate archiving
    archive_articles_qs = detect_notfound(
        articles.not_found_only_tagged()
    ).union(
        articles.release_date_tagged()
    ).union(
        articles.priority_tagged()
    )

    archive_articles.apply_async(
        ids=list(set(archive_articles_qs.values_list('pk'))),
        skip_filter=True
    )

