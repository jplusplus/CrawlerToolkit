# -*- coding: utf-8 -*-
"""
RSS Feed scraper.
Takes an url and return a list of URLs.
"""
from lxml import etree
import requests

def scrape(url):
    req = requests.get(url)
    xml = etree.fromstring(req.text.encode('utf-8'))
    _ns = xml.nsmap[None]
    if _ns and _ns.endswith('Atom'):
        # We have to setup a namespace to properly query the xml with xpath
        ns = 'http://www.w3.org/2005/Atom'
        ns_map = {'atom': ns}
        links = xml.xpath('//atom:entry/atom:link/@href', namespaces=ns_map)
    else:
        # default selector: RSS feed.
        links = xml.xpath('//item/link/text()')
    return links

