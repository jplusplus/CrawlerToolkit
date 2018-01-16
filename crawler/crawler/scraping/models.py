from django.db import models
from crawler.constants import PRESERVATION_TAGS
from crawler.scraping import managers

class PreservationTag(models.Model):
    class Meta:
        abstract = True
    article = models.ForeignKey('core.Article')

    def is_priority(self):
        return isinstance(self, PriorityTag)

    def is_release_date(self):
        return isinstance(self, ReleaseDateTag)

    def is_notfound_only(self):
        return isinstance(self, NotFoundOnlyTag)

class PriorityTag(PreservationTag):
    value = models.BooleanField()
    objects = managers.PriorityTagManager()
    @property
    def should_preserve(self):
        return self.value

class ReleaseDateTag(PreservationTag):
    value = models.DateTimeField(null=True)
    objects = managers.ReleaseDateTagManager()
    @property
    def should_preserve(self):
        return self.value is not None

class NotFoundOnlyTag(PreservationTag):
    value = models.BooleanField()
    objects = managers.NotFoundOnlyTagManager()
    @property
    def should_preserve(self):
        return self.value

PRESERVATION_TAGS_MAP = {
    PRESERVATION_TAGS.PRIORITY: PriorityTag,
    PRESERVATION_TAGS.RELEASE_DATE: ReleaseDateTag,
    PRESERVATION_TAGS.NOT_FOUND_ONLY: NotFoundOnlyTag,
}

PRESERVATION_TAGS_MAP_REVERSE = {
    v:k for k,v in PRESERVATION_TAGS_MAP.items()
}
def preservation_tag_type(model):
    _type = PRESERVATION_TAGS_MAP_REVERSE.get(model)
    if not _type:
        raise ValueError('model not recognized')
    return _type

def preservation_tag_model(tag_type):
    model = PRESERVATION_TAGS_MAP.get(tag_type)
    if not model:
        raise ValueError('tag type not recognized')
    return model
