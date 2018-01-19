import archiveis
import requests

from urllib.parse import urlparse

class Service(object):
    def __init__(self, url):
        self._url = url

    def name(self): return self.__class__.__name__
    def start(self): pass

class ArchiveORG(Service):
    def start(self):
        service_url = "{service}{url}".format(
            service='https://web.archive.org/save/',
            url=self._url)
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

class ArchiveIS(Service):
    def start(self):
        return archiveis.capture(self._url)


__services = [ ArchiveIS, ArchiveORG ]

def services(url):
    return map(lambda _: _(url), __services)
