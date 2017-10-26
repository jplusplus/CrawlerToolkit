from .settings import *
import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=500)

INSTALLED_APPS = INSTALLED_APPS + ['storages',]

ALLOWED_HOSTS = [
    'offshore-crawler.herokuapp.com',
]

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DATABASES['default'].update(db_from_env)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')

CELERY_BROKER_URL = os.getenv('REDIS_URL', '')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', '')
