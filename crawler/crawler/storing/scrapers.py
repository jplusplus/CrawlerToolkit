import re
from urllib.parse import urlparse, urljoin
from lxml import etree
import requests
from crawler.constants import RESOURCE_TYPES

def url_to_filename(url):
    path = urlparse(url).path
    return path.split('/')[-1]

def crawl_resource(page_url, url):
    get_url = url
    if not url.startswith('http'):
        parsed = urlparse(page_url)
        base = "{scheme}://{host}".format(
            scheme=parsed.scheme,
            host=parsed.hostname
        )
        if not url.startswith('/'):
            base += '/'

        get_url = urljoin(base, url)

    return {
        'url': url,
        'filename': url_to_filename(url),
        'content': requests.get(get_url).content,
        'get_url': get_url,
    }


class HTMLScraper(object):
    def __init__(self, url):
        self._url = url
        req = requests.get(url)
        self._site_url = req.url
        content = req.content
        self._html_content = content
        self._tree = etree.fromstring(content, parser=etree.HTMLParser())
        self._stylesheet_urls = self._tree.xpath('//link[@rel="stylesheet"]/@href')
        self._script_urls =  self._tree.xpath('//script/@src')
        self._image_urls =  self._tree.xpath('//img/@src')
        self._resources = dict()
        self._css_resources = dict()
        self._urls_mapping = {
            RESOURCE_TYPES.STYLE: self._stylesheet_urls,
            RESOURCE_TYPES.SCRIPT: self._script_urls,
            RESOURCE_TYPES.IMAGE: self._image_urls,
        }
        self._crawl_resources()
        self._crawl_css_resources()

    def _crawl_resources(self):
        for _, urls in self._urls_mapping.items():
            urls = self.valid_urls(urls)
            self._resources[_] = list(
                map(lambda url: crawl_resource(self._site_url, url), urls)
            )

    def _crawl_subresources(self, resource_url, urls):
        resource_dict = {
            RESOURCE_TYPES.FONT: [],
            RESOURCE_TYPES.IMAGE: [],
        }
        urls = self.valid_urls(urls)
        for origin_url in urls:
            url = origin_url
            if not url.startswith('http'):
                fn = url_to_filename(resource_url)
                base_url = resource_url.split(fn)[0]
                url = urljoin(base_url, url)

            req = requests.get(url)
            ctype = req.headers['Content-Type']
            rtype = RESOURCE_TYPES.FONT
            if ctype.startswith('image/'):
                rtype = RESOURCE_TYPES.IMAGE

            resource_dict[rtype].append({
                'url': origin_url,
                'filename': url_to_filename(origin_url),
                'content': req.content
            })

        return resource_dict

    def _crawl_css_resources(self):
        for resource in self._resources.get(RESOURCE_TYPES.STYLE):
            content = resource['content'].decode()
            sub_resource_urls = re.findall('url\("([^)]+)"\)', content)
            sub_resources = self._crawl_subresources(resource['get_url'], sub_resource_urls)
            self._css_resources[resource['url']] = sub_resources

    def valid_urls(self, urls):
        def valid_url(url):
            not_data = not url.startswith('data:')
            not_empty = len(url.strip()) > 0
            return not_data and not_empty

        return filter(valid_url, urls)

    def html_content(self, pretty_print=False):
        return self._html_content

    def static_resources(self):
        return self._resources

    def css_resources(self):
        return self._css_resources
