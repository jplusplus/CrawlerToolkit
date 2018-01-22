from .common import *
import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=500)

DEBUG = os.getenv('DEBUG', 0)
DEBUG = DEBUG != 0

HEROKU_APPNAME = os.getenv('HEROKU_APPNAME', 'offshore-crawler')

INSTALLED_APPS = INSTALLED_APPS + ['storages',]

ALLOWED_HOSTS = [
    '{app}.herokuapp.com'.format(app=HEROKU_APPNAME),
]

DOMAIN_NAME = 'https://%s' % ALLOWED_HOSTS[0]

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'crawler.storages.StaticStorage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

MEDIAFILES_LOCATION = 'archive'
DEFAULT_FILE_STORAGE = 'crawler.storages.MediaStorage'

DATABASES['default'].update(db_from_env)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')

CELERY_BROKER_URL = os.getenv('REDIS_URL', '')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', '')

# Force SSL.
SECURE_SSL_REDIRECT = True

