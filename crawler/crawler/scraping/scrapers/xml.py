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
    ns = 'http://www.w3.org/2005/Atom'
    ns_map = {'atom': ns}
    _ns = xml.nsmap[None]
    # default selector: RSS feed.
    if _ns and _ns.endswith('Atom'):
        links = xml.xpath('//atom:entry/atom:link/@href')
    else:
        links = xml.xpath('//item/link/text()')
    return links
