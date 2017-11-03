import archiveis
import requests

from urllib.parse import urlparse

def archiveorg_service(url):
    service_url = "{service}{url}".format(
        service='https://web.archive.org/save/',
        url=url)
    archived_url = None
    req = requests.post(service_url)
    parsed = urlparse(req.url)
    headers = req.headers
    content_location = headers.get('Content-Location')
    if content_location:
        archived_url = "{scheme}://{domain}{place}".format(
            scheme=parsed.scheme,
            domain=parsed.hostname,
            place=content_location
        )

    return archived_url

def archiveis_service(url):
    return archiveis.capture(url)

def services(url):
    return [
        lambda: archiveis_service(url),
        lambda: archiveorg_service(url)
    ]

