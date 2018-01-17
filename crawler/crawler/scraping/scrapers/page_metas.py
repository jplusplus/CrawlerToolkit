from lxml import etree
import requests

def scrape(url):
    req = requests.get(url)
    parser = etree.HTMLParser()
    tree = etree.fromstring(req.text.encode('utf-8'), parser)
    ogtitle = tree.xpath('///meta[@property="og:title"]/@content')
    maintitle = tree.xpath('/head/title/text()')
    if len(ogtitle) > 0:
        title = ogtitle[0]
    else:
        title = maintitle[0]
    all_tags = tree.xpath('//head/meta[starts-with(@name, \'preservation\')]')
    tags = list(map(
        lambda tag: {
            'type': tag.attrib['name'],
            'value': tag.attrib['content']
        }, all_tags))

    return [ title, tags ]

