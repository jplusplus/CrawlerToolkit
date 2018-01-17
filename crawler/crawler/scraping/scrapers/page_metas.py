from lxml import etree
import requests

def parse(html):
    parser = etree.HTMLParser()
    title = None
    tree = etree.fromstring(html, parser)
    ogtitle = tree.xpath('///meta[@property="og:title"]/@content')
    maintitle = tree.xpath('//head/title/text()')
    if len(ogtitle) > 0:
        title = ogtitle[0]
    elif len(maintitle):
        title = maintitle[0]

    all_tags = tree.xpath('//head/meta[starts-with(@name, \'preservation\')]')
    tags = list(map(
        lambda tag: {
            'type': tag.attrib['name'],
            'value': tag.attrib['content']
        }, all_tags))

    return [ title, tags ]


def scrape(url):
    req = requests.get(url)
    return parse(req.text.encode('utf-8'))

