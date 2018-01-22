from importlib import import_module
from django.conf import settings
from django.template import Library
from crawler.core.models import Feed, Article
from crawler.constants import STATES

register = Library()

def get_admin_site():
    site_module = getattr(
        settings,
        'MATERIAL_ADMIN_SITE',
        'django.contrib.admin.site'
    )
    mod, inst = site_module.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, inst)

site = get_admin_site()

def configure_row(title, qs, icon):
    return {
        'title': title,
        'value': qs.count(),
        'icon': icon,
    }


def feed_row():
    active_feeds = Feed.objects.filter(active=True)
    return configure_row(
        title='Sources monitored',
        qs=active_feeds,
        icon='rss_feed',
    )

def articles_rows():
    ARCHIVED = STATES.ARCHIVE.ARCHIVED
    STORED = STATES.PRESERVATION.STORED
    crawled = Article.objects.exclude(crawled_at=None)
    archived = Article.objects.filter(archiving_state=ARCHIVED)
    stored = Article.objects.exclude(archiving_state=ARCHIVED)\
        .filter(preservation_state=STORED)

    crawled_row = configure_row(
        title='Articles crawled since begining',
        qs=crawled,
        icon='find_in_page'
    )
    archived_row = configure_row(
        title='Articles archived',
        qs=archived,
        icon='save'
    )
    stored_row = configure_row(
        title='Articles stored for future archiving',
        qs=stored,
        icon='cached'
    )
    return [
        crawled_row,
        archived_row,
        stored_row,
    ]


@register.assignment_tag
def get_dashboard_rows(request):
    rows = [
        feed_row(),
    ] + articles_rows()
    return rows



