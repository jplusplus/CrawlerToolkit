from datetime import datetime
import re
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery.contrib import rdb
from django.core.files.storage import default_storage as storage
from uuid import uuid4

from celery.decorators import task
from crawler.celery import app
from crawler.constants import STATES, RESOURCE_TYPES

# Scrapers 
from .scrapers import HTMLScraper

logger = get_task_logger(__name__)

def save_resource(article, resource, use_tdir=True, uniq_fn=True):
    fn = resource['filename']
    content = resource['content']
    path = article.resource_path(fn, use_tdir=use_tdir, uniq_fn=uniq_fn)
    f = storage.open(path)
    f.write(content)
    f.close()
    resource['hosted_url'] = path
    return resource

@task
def delete_resource_dir(path):
    storage.deletedir(path)

def delete_articles_resources(articles):
    delete_resource_dir.map(map(lambda a: a.resources_dir(), articles))

def scrape_article_resources(url):
    scraper = HTMLScraper(url)
    html_content = scraper.html_content()
    html_resources = scraper.static_resources()
    css_resources = scraper.css_resources()
    # logger.info("sraped article")
    return [ html_content, html_resources, css_resources ]

def as_hosted_content(content, resources):
    def multiple_replace(txt, _dict):
        rx = re.compile('|'.join(map(re.escape, _dict)))
        def one_xlat(match):
            return _dict[match.group(0)]
        return rx.sub(one_xlat, txt)

    content = content.decode()
    if len(resources) > 0:
        mapped_urls = {
            resource['url']: mediaurl(resource['hosted_url']) for resource in resources
        }
        content = multiple_replace(content, mapped_urls)
    return bytes(content, 'utf-8')

def process_css(css, resources):
    content = css['content']
    resources_dict = resources[css['url']]
    resources_list = list()
    for rtype, sub_resources in resources_dict.items():
        sub_resources_list += map(
            lambda res: save_resource(article, res, rtype=rtype),
            sub_resources
        )
    return as_hosted_content(content, resources_list)

def save_resources(article, resources_dict, css_resources):
    article_resources = list()
    for ressource_type, resources in resources_dict.items():
        for resource_dict in resources:
            if rtype == RESOURCE_TYPES.STYLE:
                resource_dict['content'] = process_css(resource_dict, css_resources)
            article_resources.append(
                save_resource(article, resource_dict, rtype=rtype)
            )
    return article_resources

def crawl_article_resources(article):
    [ html_content, resources, css_resources ] = scrape_article_resources(
        article.url
    )
    resources = save_resources(article, resources, css_resources)
    save_resource(
        article,
        {
            'filename': 'index.html',
            'content': as_hoted_content(html_content, resources),
        },
        use_tdir=False,
        uniq_fn=False
    )
    article.preservation_state = STATES.PRESERVATION.STORED
    article.save()
    return pk

@task
def crawl_resources(ids):
    logger.info('recieved ids %s' % ids)
    from crawler.utils import pickattr
    from crawler.core import tasks_utils
    from crawler.constants import STATES
    articles = tasks_utils.articles(
        pickattr(tasks_utils.should_be_preserved(ids), 'pk')
    )
    articles.update(preservation_state=STATES.PRESERVATION.PRESERVING)
    map(crawl_article_resources, articles)
    return ids

