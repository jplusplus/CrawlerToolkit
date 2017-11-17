from django.db import connection
from django.conf import settings
from urllib.parse import urlparse
from pprint import pprint

def pickattr(qs, attrname):
    return list(map(lambda obj:getattr(obj, attrname), qs))

def absurl(path):
    return "{domain}{path}".format(
        domain=settings.DOMAIN_NAME,
        path=path
    )

def mediaurl(path):
    s3_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN')
    base_url = settings.DOMAIN_NAME
    if s3_domain != '':
        base_url = 'https://{domain}'.format(domain=s3_domain)

    url = path
    parsed_path = urlparse(path)
    if not path.startswith('http'):
        url = '{domain}{path}'.format(domain=base_url, path=path)

    if len(parsed_path.query) > 0:
        url = "{url}?{query}".format(url=url, query=parsed_path.query)

    return url



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


def print_counts(**kwargs):
    todict = lambda c: {
        "%s.%s" % (c[0]._meta.app_label, c[0]._meta.verbose_name): c[1]
    }
    pprint(
        list(map(todict, modelcounts(**kwargs)))
    )
