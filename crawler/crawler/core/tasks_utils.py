from datetime import datetime
from django.db import transaction
from crawler.constants import PRESERVATION_TAGS
import re

def active_feeds():
    from crawler.core.models import Feed
    return Feed.objects.active_feeds()

def crawl_feeds(feeds):
    from crawler.scraping.tasks import crawl_feeds as _crawl, crawl_articles_preservation_tags
    created_articles = save_feeds_urls(_crawl(feeds))
    preservation_tags = crawl_articles_preservation_tags(created_articles)
    save_articles_preservation_tags(preservation_tags)

def crawl_feed(feed):
    return crawl_feeds([feed])

def save_feeds_urls(feeds_urls):
    from crawler.core.models import Article
    """
    Save the given feeds_urls and makes sure not to try to save already
    existing url.

    Parameters:
        - feeds_urls, array of urls structured like this [
            [ <feed pk>, <url> ],
            [ <feed pk>, <url> ],
            ...
          ]
    """
    urls = list(map(lambda url: url[1], feeds_urls))
    already_existing_urls = Article.objects.clashing_urls(urls)
    feeds_urls = list(
        filter(lambda url: url[1] not in already_existing_urls,feeds_urls)
    )
    urls_to_create = dict()
    feeds_urls_to_create = list()
    for feed_url in feeds_urls:
        if not urls_to_create.get(feed_url[1], False):
            urls_to_create[feed_url[1]] = True
            feeds_urls_to_create.append(feed_url)
    with transaction.atomic():
        created = map(lambda url: Article.objects.create(url=url[1], feed_id=url[0]),
            feeds_urls_to_create)

    return created


def save_articles_preservation_tags(preservation_tags):
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



