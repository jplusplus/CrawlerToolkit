from datetime import datetime
import re

from celery.utils.log import get_task_logger

from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile
from crawler.constants import PRESERVATION_TAGS, STATES
from crawler.utils import pickattr, mediaurl

logger = get_task_logger(__name__)

def filter_not_needed_tags(qs):
    return qs.exclude(
            article__archiving_state=STATES.ARCHIVE.ARCHIVED
        ).exclude(
            article__preservation_state=STATES.PRESERVATION.NO_PRESERVE
        )

def qs_or_ids(qs, f):
    if not qs or len(qs) == 0: return qs
    if type(qs[0]) == type(0):
        qs  = f(qs)
    return qs

def should_be_preserved(qs):
    qs = qs_or_ids(qs, articles)
    return list(filter(lambda a: a.should_preserve, qs))

def should_be_archived(qs):
    from crawler.core.models import ReleaseDateTag, PriorityTag, Article
    qs = qs_or_ids(qs, articles)
    rids = pickattr(
        ReleaseDateTag.objects.filter(
            article__in=qs,
            value__lte=timezone.now()
        ), 'article_id')
    pids = pickattr(
        PriorityTag.objects.filter(
            article__in=qs,
            value=True
        ), 'article_id')
    ids = list(set(rids + pids))
    return Article.objects.filter(
            pk__in=ids
        ).exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVED
        )
def priority_articles():
    from crawler.core.models import PriorityTag
    tags = PriorityTag.objects.filter(value=True)
    tags = filter_not_needed_tags(tags)
    return pickattr(tags, 'article')

def notfound_only_articles():
    from crawler.core.models import NotFoundOnlyTag
    tags = NotFoundOnlyTag.objects.filter(value=True)
    tags = filter_not_needed_tags(tags)
    return pickattr(tags, 'article')

def release_date_articles():
    from crawler.core.models import ReleaseDateTag
    tags = ReleaseDateTag.objects.filter(value__lte=timezone.now())
    tags = filter_not_needed_tags(tags)
    return pickattr(tags, 'article')

def filter_by_id(Model,ids):return Model.objects.filter(pk__in=ids)

def feeds(ids):
    from crawler.core.models import Feed
    return filter_by_id(Feed, ids)

def articles(ids):
    from crawler.core.models import Article
    return filter_by_id(Article, ids)

def active_feeds():
    from crawler.core.models import Feed
    return Feed.objects.active_feeds()

def create_articles(articles_urls):
    from crawler.core.models import Article
    """
    Save the given articles_urls and makes sure not to try to save already
    existing url.

    Parameters:
        - articles_urls, array of urls structured like this [
            [ <feed pk>, <url> ],
            [ <feed pk>, <url> ],
            ...
          ]
    """
    urls = list(map(lambda url: url[1], articles_urls))
    already_existing_urls = Article.objects.clashing_urls(urls)
    articles_urls = list(
        filter(lambda url: url[1] not in already_existing_urls,articles_urls)
    )

    urls_to_create = dict()
    articles_urls_to_create = list()
    for feed_id, url in articles_urls:
        if not urls_to_create.get(url, False):
            urls_to_create[url] = True
            articles_urls_to_create.append([feed_id, url])

    with transaction.atomic():
        created = list(
            map(
                lambda _: Article.objects.create(url=_[1], feed_id=_[0]),
                articles_urls_to_create
            )
        )
    return created

def reset_articles_states(articles):
    if getattr(articles, 'update', None):
        articles.update(archiving_state=None)
        articles.update(preservation_state='')
    else:
        for a in articles:
            a.preservation_state = ''
            a.archiving_state = None
            a.save()

def delete_resources_of(articles):
    return [ article.deletedir() for article in articles ]

def delete_tags_of(articles):
    from crawler.core import models
    tags = models.PriorityTag.objects.filter(article__in=articles)
    tags = tags.union(models.ReleaseDateTag.objects.filter(article__in=articles))
    tags = tags.union(models.NotFoundOnlyTag.objects.filter(article__in=articles))

    return [ tag.delete() for tag in tags ]

def delete_archived_urls_of(articles):
    from crawler.archiving.models import ArchivedArticle
    urls = ArchivedArticle.objects.filter(article__in=articles)
    return [ url.delete() for url in urls ]

def set_articles_crawled(articles):
    for article in articles:
        article.crawled_at = timezone.now()
        if not article.should_preserve:
            article.preservation_state = STATES.PRESERVATION.NO_PRESERVE
        elif article.preservation_state is not STATES.PRESERVATION.STORED:
            article.preservation_state = STATES.PRESERVATION.PRESERVE
        article.save()

def save_preservation_tags(preservation_tags):
    from crawler.core.models import Article, PriorityTag, ReleaseDateTag, NotFoundOnlyTag

    date_pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    def strtobool(original_value):
        value = original_value.strip()
        if value == 'true':
            value = True
        else:
            value = False

        print("strtobool(%s) - %s" % (original_value, value))
        return value

    tags = []
    def create_priority_tag(article_id, value):
        return PriorityTag.objects.create(
                article_id=article_id,
                value=strtobool(value))

    def create_release_date_tag(article_id, value):
        if date_pattern.match(value):
            value = datetime.strptime(value, '%Y-%m-%d')
        else:
            value = None
        return ReleaseDateTag.objects.create(
                article_id=article_id,
                value=value)

    def create_notfound_only_tag(article_id, value):
        return NotFoundOnlyTag.objects.create(
                article_id=article_id,
                value=strtobool(value))

    types = {
        PRESERVATION_TAGS.PRIORITY: create_priority_tag,
        PRESERVATION_TAGS.RELEASE_DATE: create_release_date_tag,
        PRESERVATION_TAGS.NOT_FOUND_ONLY: create_notfound_only_tag
    }

    with transaction.atomic():
        for [article_id, tag_dict] in preservation_tags:
            ptype = tag_dict['type']
            create_tag = types.get(ptype, None)
            if not create_tag:
                raise ValueError('meta tag type %s not recognized' % ptype)
            tag = create_tag(article_id, tag_dict['value'])
            tags.append(tag)
    return tags



