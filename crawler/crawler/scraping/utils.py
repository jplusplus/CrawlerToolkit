import re

from django.utils import timezone
from crawler.scraping.models import PriorityTag, ReleaseDateTag, NotFoundOnlyTag
from crawler.utils import strtobool
from crawler.constants import PRESERVATION_TAGS

date_pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")

def save_preservation_tags(preservation_tags):
    tags = []
    def create_priority_tag(article_id, value):
        return PriorityTag.objects.create(
            article_id=article_id,
            value=strtobool(value)
        )

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

