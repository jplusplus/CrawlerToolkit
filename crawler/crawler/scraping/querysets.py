from django.db.models import query
from django.utils import timezone

class PreservationTagQuerySet(query.QuerySet):
    def should_be_preserved(self):
        raise NotImplementedError('Must implement should_be_preserved')

class BoolTagMixin(object):
    def should_be_preserved(self): return self.filter(value=True)

class PriorityTagQuerySet(PreservationTagQuerySet, BoolTagMixin): pass
class NotFoundOnlyTagQuerySet(PreservationTagQuerySet, BoolTagMixin): pass

class ReleaseDateTagQuerySet(PreservationTagQuerySet):
    def should_be_preserved(self):
        return self.filter(value__lte=timezone.now())

