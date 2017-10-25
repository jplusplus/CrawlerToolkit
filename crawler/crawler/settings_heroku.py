from .settings import *
import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=500)

DATABASES['default'].update(db_from_env)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')

CELERY_BROKER_URL = os.getenv('REDIS_URL', '')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', '')
