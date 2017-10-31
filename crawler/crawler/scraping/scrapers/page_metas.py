from lxml import etree
import requests

def scrape(url):
    req = requests.get(url)
    parser = etree.HTMLParser()
    tree = etree.fromstring(req.text.encode('utf-8'), parser)

    all_tags = tree.xpath('//head/meta[starts-with(@name, \'preservation\')]')
    return list(map(
        lambda tag: {
            'type': tag.attrib['name'],
            'value': tag.attrib['content']
        }, all_tags))

