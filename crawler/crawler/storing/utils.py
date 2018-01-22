from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage

from celery.contrib import rdb

from urllib.parse import urlparse
import re

from crawler.utils import absurl
from crawler.constants import RESOURCE_TYPES

def mediaurl(path):
    media_url = getattr(settings, 'MEDIA_URL')
    path = '{media}{path}'.format(
        media=media_url,
        path=path
    )
    if not path.startswith('http'):
        path = absurl(path)

    return path


def as_hosted_content(content, resources):
    """
    Produce suitabled "hosted" version of a text file.
    It can remplace a list of URLs based on dict map.
    """
    def multiple_replace(txt, _dict):
        rx = re.compile('|'.join(map(re.escape, _dict)))
        def one_xlat(match):
            return _dict[match.group(0)]
        return rx.sub(one_xlat, txt)

    if type(content) == type(b''):
        content = content.decode()

    if len(resources) > 0:
        mapped_urls = {
            resource['url']: resource['hosted_url'] for resource in resources
        }
        content = multiple_replace(content, mapped_urls)
    return bytes(content, 'utf-8')

def save_html(article, html, resources):
    return save_resource(
        article,
        {
            'filename': 'index.html',
            'content': as_hosted_content(html, resources)
        },
        use_tdir=False,
        uniq_fn=False
    )

def save_resource(
        article,
        resource,
        use_tdir=True,
        uniq_fn=True,
        resource_type=None
    ):
    fn = resource['filename']
    content = resource['content']
    path = article.resource_path(
        fn,
        use_tdir=use_tdir,
        uniq_fn=uniq_fn,
        resource_type=resource_type
    )
    f = storage.save(path, ContentFile(content))


    resource['hosted_url'] = mediaurl(path)
    return resource

def save_static_resources(article, static_resources):
    saved_resources = list()

    if static_resources.get('content'):
        static_resources = { None: [ static_resources ] }

    for resource_type, resources in static_resources.items():
        for resource_dict in resources:
            if resource_dict.get('resources'):
                sub_resources = save_static_resources(article, resource_dict['resources'])
                resource_dict['content'] = as_hosted_content(
                    resource_dict['content'],
                    sub_resources
                )
                saved_resources = saved_resources + sub_resources

            uniq_fn = resource_dict.get('uniq_fn', True)
            use_tdir = resource_dict.get('use_tdir', True)
            saved_resources.append(
                save_resource(
                    article,
                    resource_dict,
                    resource_type=resource_type,
                    use_tdir=use_tdir,
                    uniq_fn=uniq_fn
                )
            )
    return saved_resources

def save_article_resources(article, scraper):
    content = scraper.content()
    content['filename'] = 'index.html'
    content['use_tdir'] = False
    content['uniq_fn'] = False
    save_static_resources(article, content)
