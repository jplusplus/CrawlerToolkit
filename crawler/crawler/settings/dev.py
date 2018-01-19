from .common import *

DOMAIN_NAME = 'http://localhost:4000'
CELERY_BROKER_URL = 'redis://localhost:3000'
CELERY_RESULT_BACKEND = 'redis://localhost:3000'

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')

DEFAULT_FILE_STORAGE = 'crawler.storages.LocalMediaStorage'

