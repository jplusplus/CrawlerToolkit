from crawler.constants import PRESERVATION_TAGS
from crawler.core import inherithance
from django.db import models

class PreservationTag(inherithance.ParentModel):
    article = models.ForeignKey('Article', related_name='preservation_tags')
    @property
    def should_preserve(self):
        return self.as_leaf_class().should_preserve

    def _is_type(self, model_type):
        return isinstance(self.as_leaf_class(), model_type)

    def is_release_date(self): return self._is_type(ReleaseDateTag)

    def is_priority(self): return self._is_type(PriorityTag)

    def is_notfound_only(self): return self._is_type(NotFoundOnlyTag)

class PriorityTag(PreservationTag):
    value = models.BooleanField()
    @property
    def should_preserve(self):
        return self.value

class ReleaseDateTag(PreservationTag):
    value = models.DateTimeField(null=True)
    @property
    def should_preserve(self):
        return self.value is not None

class NotFoundOnlyTag(PreservationTag):
    value = models.BooleanField()
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

