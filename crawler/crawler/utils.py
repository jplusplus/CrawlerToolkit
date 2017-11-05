from django.conf import settings
from urllib.parse import urlparse

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

    parsed_path = urlparse(path)
    url = '{domain}{path}'.format(domain=base_url, path=path)

    if len(parsed_path.query) > 0:
        url = "{url}?{query}".format(url=url, query=parsed_path.query)

    return url
