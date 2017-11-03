from django.conf import settings

def pickattr(qs, attrname):
    return list(map(lambda obj:getattr(obj, attrname), qs))

def absurl(path):
    return "{domain}{path}".format(
        domain=settings.DOMAIN_NAME,
        path=path
    )

def mediaurl(path):
    base_url = settings.MEDIA_URL
    if not base_url.startswith('http'):
        base_url = '{domain}{path}'.format(
            domain=settings.DOMAIN_NAME,
            path=base_url
        )
    return '{domain}{path}'.format(domain=base_url, path=path)
