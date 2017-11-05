from django.core.validators import URLValidator
import re

twitter_patt = re.compile('https://twitter.com/\w+$')

valid_url = URLValidator(schemes=['http','https'])

def valid_feed_url(value):
    valid_url(value)
    is_xml_feed = value.endswith('.xml')
    is_twitter_account = twitter_patt.match(value)
    if not (is_twitter_account or is_xml_feed):
        raise ValidationError((
            '%s is not a valid feed URL. It must either be twitter account URL'
            '(ex: https://twitter.com/toutenrab) or an RSS feed address '
            '(ex: http://www.lemonde.fr/rss/une.xml)'
        ) % value)
