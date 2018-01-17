from django.db import models
from crawler.constants import PRESERVATION_TAGS
from crawler.scraping import querysets


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

class PreservationTagManager(models.Manager):
    def queryset_class(self):
        return MODEL_QUERYSET_MAP[self.model]

    def get_queryset(self):
        QuerySet = self.queryset_class()
        return QuerySet(self.model)

class PriorityTag(PreservationTag):
    value = models.BooleanField()
    objects = PreservationTagManager()
    @property
    def should_preserve(self):
        return self.value

class ReleaseDateTag(PreservationTag):
    value = models.DateTimeField(null=True)
    objects = PreservationTagManager()

    @property
    def should_preserve(self):
        return self.value is not None

class NotFoundOnlyTag(PreservationTag):
    value = models.BooleanField()
    objects = PreservationTagManager()
    @property
    def should_preserve(self):
        return self.value

MODEL_QUERYSET_MAP = {
    PriorityTag: querysets.PriorityTagQuerySet,
    ReleaseDateTag: querysets.ReleaseDateTagQuerySet,
    NotFoundOnlyTag: querysets.NotFoundOnlyTagQuerySet
}



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
