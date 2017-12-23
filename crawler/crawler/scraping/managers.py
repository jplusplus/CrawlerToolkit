from django.db import models
from django.utils import timezone

class PreservationTagManager(models.Manager):
    def should_preserve(self): raise Error('Must implement should_preserve')

class BoolMixin(object):
    def should_preserve(self):
        return self.get_queryset().filter(value=True)

class PriorityTagManager(PreservationTagManager, BoolMixin): pass
class NotFoundOnlyTagManager(PreservationTagManager, BoolMixin): pass

class ReleaseDateTagManager(PreservationTagManager):
    def should_preserve(self):
        return self.get_querset().filter(value__lte=timezone.now())

