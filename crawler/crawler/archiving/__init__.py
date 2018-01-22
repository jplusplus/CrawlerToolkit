from crawler.archiving import services as archive
from crawler.archiving.models import ArchivedArticle
from crawler.archiving.scrapers import detect_notfound

from crawler.constants import STATES

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
