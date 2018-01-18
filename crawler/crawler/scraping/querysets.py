from django.db.models import query
from django.utils import timezone

class PreservationTagQuerySet(query.QuerySet):
    def should_be_preserved(self):
        raise NotImplementedError('Must implement should_be_preserved')

class PriorityTagQuerySet(PreservationTagQuerySet):
    def should_be_preserved(self): return self.filter(value=True)

class NotFoundOnlyTagQuerySet(PreservationTagQuerySet):
    def should_be_preserved(self): return self.filter(value=True)

class ReleaseDateTagQuerySet(PreservationTagQuerySet):
    def should_be_preserved(self):
        return self.filter(value__lte=timezone.now())

