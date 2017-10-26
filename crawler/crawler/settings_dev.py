from .settings import *

CELERY_BROKER_URL = 'redis://localhost:3000'
CELERY_RESULT_BACKEND = 'redis://localhost:3000'

STATIC_ROOT = os.path.join(BASE_DIR, 'storage')
