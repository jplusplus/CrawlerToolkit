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
    return xml.xpath('//item/link/text()')
