from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# set the default settings module for celery.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawler.settings')

app = Celery('tasks')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Will load tasks from all installed application (see
# `crawler.settings.INSTALLED_APPS` list).
app.autodiscover_tasks()
