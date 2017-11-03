import re
from urllib.parse import urlparse, urljoin
from lxml import etree
import requests
from crawler.constants import RESOURCE_TYPES

def url_to_filename(url):
    path = urlparse(url).path
    return path.split('/')[-1]

def crawl_resource(url):
    return {
        'url': url,
        'filename': url_to_filename(url),
        'content': requests.get(url).content,
    }

class HTMLScraper(object):
    def __init__(self, url):
        self._url = url
        self._tree = etree.parse(url, parser=etree.HTMLParser())
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
            self._resources[_] = list(map(crawl_resource, urls))

    def _crawl_subresources(self, resource_url, urls):
        resource_dict = {
            RESOURCE_TYPES.FONT: [],
            RESOURCE_TYPES.IMAGE: [],
        }
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
            sub_resources = self._crawl_subresources(resource['url'], sub_resource_urls)
            self._css_resources[resource['url']] = sub_resources

    def html_content(self, pretty_print=False):
        return etree.tostring(self._tree, pretty_print=pretty_print)

    def static_resources(self):
        return self._resources

    def css_resources(self):
        return self._css_resources
