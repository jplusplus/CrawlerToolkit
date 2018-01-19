from django.urls import reverse
from celery.decorators import task
from celery.utils import log
from crawler import utils
from crawler.archiving import archive_article, detect_notfound
from crawler.archiving.models import ArchivedArticle

logger = log.get_task_logger(__name__)

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
    archived = list()
    articles = Article.objects.ids(ids)
    if not skip_filter:
        articles = articles.should_be_archived()

    articles.set_archiving()
    for article in articles:
        try:
            archive_article(article)
        except Exception as e:
            logger.error('An error occured while archiving article', e)

    return list(map(__archive_article, articles))

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

