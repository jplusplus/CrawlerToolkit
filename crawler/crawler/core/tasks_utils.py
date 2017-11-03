from datetime import datetime
import re

from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile
from crawler.constants import PRESERVATION_TAGS, STATES
from crawler.utils import pickattr, mediaurl

TXT_RESOURCES_PATTERN = re.compile('.+\.(html|js|css)$')

def filter_not_needed_tags(qs):
    return qs.exclude(
        article__preservation_state=STATES.PRESERVATION.NO_PRESERVE,
        article__archiving_state=STATES.ARCHIVE.ARCHIVED
    )

def should_be_preserved(articles):
    return list(filter(lambda a: a.should_preserve, articles))

def should_be_archived(articles):
    from crawler.core.models import ReleaseDateTag, PriorityTag, Article
    article_ids = pickattr(articles, 'pk')
    rids = pickattr(
        ReleaseDateTag.objects.filter(
            article_id__in=article_ids,
            value__lte=timezone.now()
        ), 'article_id')
    pids = pickattr(
        PriorityTag.objects.filter(
            article_id__in=article_ids,
            value=True
        ), 'article_id')
    ids = list(set(rids + pids))
    return Article.objects.filter(pk__in=ids)

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

def crawl_feeds(feeds):
    from crawler.scraping.tasks import crawl_feeds as _crawl
    _crawl.delay(feed_ids=pickattr(feeds, 'pk'))

def crawl_feed(feed):
    return crawl_feeds([feed])

def crawl_articles(articles):
    from crawler.constants import STATES
    from crawler.scraping.tasks import crawl_articles as _crawl
    _crawl.delay(pickattr(articles, 'pk'))


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

def delete_tags_of(ids):
    from crawler.core.models import PreservationTag
    tags = PreservationTag.objects.filter(article_id__in=ids)
    [ tag.delete() for tag in tags]

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

def as_hosted_html(html, resources):
    def multiple_replace(txt, _dict):
        rx = re.compile('|'.join(map(re.escape, _dict)))
        def one_xlat(match):
            return _dict[match.group(0)]
        return rx.sub(one_xlat, txt)

    mapped_urls = {
        resource.url: mediaurl(resource.resource_file.url) for resource in resources
    }
    return multiple_replace(html.decode(), mapped_urls)

def create_or_update_resources(article, resources_dict):
    def get_resource_model(resource_type):
        from crawler.core.resource_models import RESOURCE_TYPES_MAP
        model = RESOURCE_TYPES_MAP.get(resource_type)
        if not model:
            raise ValueError(
                 '%s is not a recognized resource type' % resource_type
            )
        return model

    for ressource_type, resources in resources_dict.items():
        ResourceModel = get_resource_model(ressource_type)
        for resource_dict in resources:
            resource = ResourceModel(
                url=resource_dict['url'],
                article=article,
            )
            fn = resource_dict['filename']
            content = resource_dict['content']
            if TXT_RESOURCES_PATTERN.match(fn):
                content = content.decode()

            resource.set_content(fn, content)

def save_resources(article, html_content, resources_dict):
    from crawler.core.models import HTMLResource
    create_or_update_resources(article, resources_dict)
    resources = article.resources.all()
    hosted_html = as_hosted_html(html_content, resources)

    if article.has_html_content():
        article.html_content().set_content('index.html', hosted_html)
    else:
        html_file = HTMLResource.objects.create(
            use_unique_name=False,
            use_resource_type_dir=False,
            article=article)
        html_file.set_content('index.html', hosted_html)

    article.preservation_state = STATES.PRESERVATION.STORED
    article.save()
