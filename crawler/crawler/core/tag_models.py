from crawler.core import inherithance
from django.db import models

class PreservationTag(inherithance.ParentModel):
    article = models.ForeignKey('Article', related_name='preservation_tags')
    @property
    def should_preserve(self):
        return self.as_leaf_class().should_preserve


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

