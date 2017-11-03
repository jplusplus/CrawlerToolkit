from lxml import etree
import requests

from django.templatetags.static import static
from django.conf import settings

def as_hosted_html(html, resources):
    def resource_url(resource):
        return "{root}{path}".format(root=settings.MEDIA_URL,path=resource.path)

    def multiple_replace(txt, _dict):
        rx = re.compile('|'.join(map(re.escape, _dict)))
        def one_xlat(match):
            return _dict[match.group(0)]

        return rx.sub(one_xlat, text)

    mapped_urls = {
        resource.url: resource_url(resource) for resource in resources
    }
    return multiple_replace(html, mapped_urls)

def page_ressources_urls(url):
    """
    Return an array of resources URL
    """
    tree = etree.parse(url, parser = etree.HTMLParser())
    stylesheets = tree.xpath('//link[@rel="stylesheet"]/@href')
    javascripts = tree.xpath('//script/@src')
    images = tree.xpath('//img/@src')
    resources = stylesheets + javascripts + images
    return resources

def crawl_resources(urls):
    resources = list()
    for url in urls:
        req = requests.get(url)
        storage.
