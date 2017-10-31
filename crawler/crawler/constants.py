# Plain Old Python Object
class POPO(object): pass

class States(object):
    def __init__(self, states, *args, **kwargs):
        for (name, label) in states:
            setattr(self, name, name)
        self.states = states;

    def list(self): return self.states;


STATES = POPO()

STATES.CRAWL = States((
    ('CRAWLED', 'Crawled'),
    ('CRAWLING','Crawling in progress'),
    ('PROGRAMMED', 'Crawling programmed'),
))


STATES.ARCHIVE = States((
    ('ARCHIVED', 'Archived'),
    ('ARCHIVING', 'Archiving in progress'),
    ('NO_ARCHIVING', 'No archiving is needed'),
))


PRESERVATION_TAGS = POPO()
PRESERVATION_TAGS.PRIORITY = 'preservation:priority'
PRESERVATION_TAGS.RELEASE_DATE = 'preservation:release_date'
PRESERVATION_TAGS.NOT_FOUND_ONLY = 'preservation:notfound_only'

FEED_TYPES = POPO()
FEED_TYPES.TWITTER = 'TWITTER'
FEED_TYPES.RSS = 'RSS'
