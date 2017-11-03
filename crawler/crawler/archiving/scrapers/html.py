from lxml import etree
import requests
from crawler.constants import RESOURCE_TYPES

class HTMLScraper(object):
    def __init__(self, url):
        self.tree = etree.parse(url, parser=etree.HTMLParser())

    def html_content(self, pretty_print=False):
        return etree.tostring(self.tree, pretty_print=pretty_print)

    def static_resources(self):
        def crawl_resource(url):
            return {
                'url': url,
                'filename': url.split('/')[-1],
                'content': requests.get(url).content,
            }
        resources_dict = {
            RESOURCE_TYPES.STYLE: self.tree.xpath('//link[@rel="stylesheet"]/@href'),
            RESOURCE_TYPES.SCRIPT: self.tree.xpath('//script/@src'),
            RESOURCE_TYPES.IMAGE: self.tree.xpath('//img/@src'),
        }

        for _, urls in resources_dict.items():
            resources_dict[_] = map(crawl_resource, urls)
        print("Scrapped resources %s" % resources_dict)
        return resources_dict
