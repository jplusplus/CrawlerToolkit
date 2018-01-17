from django.db import connection
from django.conf import settings
from urllib.parse import urlparse
from pprint import pprint

# Plain Old Python Object
class POPO(object): pass

def pickattr(qs, attrname):
    return list(map(lambda obj:getattr(obj, attrname), qs))

def absurl(path): # pragma: nocover
    return "{domain}{path}".format(
        domain=settings.DOMAIN_NAME,
        path=path
    )

def modelcounts(sort=False, reverse=True):
    count = lambda model: (
        model, model.objects.count() if getattr(model, 'objects', None) else 0
    )
    tables = connection.introspection.table_names()
    modelclasses = connection.introspection.installed_models(tables)
    counts =  map(count, modelclasses)
    if sort:
        order = -1 if reverse else 1
        counts = sorted(counts, key=lambda e: order * e[1])

    return counts

def strtobool(original_value):
    value = original_value.strip().lower()
    if value == 'true':
        value = True
    else:
        value = False
    return value

def print_counts(**kwargs):
    todict = lambda c: {
        "%s.%s" % (c[0]._meta.app_label, c[0]._meta.verbose_name): c[1]
    }
    pprint(
        list(map(todict, modelcounts(**kwargs)))
    )
