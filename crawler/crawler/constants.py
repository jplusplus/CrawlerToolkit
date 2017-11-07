# Plain Old Python Object
class POPO(object): pass

class States(object):
    def __init__(self, states, *args, **kwargs):
        self.labels_dict = dict()
        for (name, label) in states:
            self.labels_dict[name] = label
            setattr(self, name, name)
        self.states = states;

    def label(self, state): return self.labels_dict[state]

    def list(self): return self.states;


STATES = POPO()

STATES.CRAWL = States((
    ('CRAWLED', 'Crawled'),
    ('ERROR','There has been an error during crawling'),
    ('PROGRAMMED', 'Crawling programmed'),
))

PRESERVATION_STATES = States((
    ('PRESERVE', 'Should preserve'),
    ('STORED', 'Has been stored'),
    ('NO_PRESERVE', 'Not required'),
))

STATES.PRESERVATION = PRESERVATION_STATES

STATES.ARCHIVE = States((
    ('ARCHIVED', 'Archived'),
    ('ARCHIVING', 'Archiving'),
    ('ERROR', 'An error occured'),
))


PRESERVATION_TAGS = POPO()
PRESERVATION_TAGS.PRIORITY = 'preservation:priority'
PRESERVATION_TAGS.RELEASE_DATE = 'preservation:release_date'
PRESERVATION_TAGS.NOT_FOUND_ONLY = 'preservation:notfound_only'


RESOURCE_TYPES = POPO()
RESOURCE_TYPES.SCRIPT = 'script'
RESOURCE_TYPES.STYLE = 'stylesheet'
RESOURCE_TYPES.IMAGE = 'image'
RESOURCE_TYPES.HTML = 'html'
RESOURCE_TYPES.FONT = 'font'

FEED_TYPES = POPO()
FEED_TYPES.TWITTER = 'TWITTER'
FEED_TYPES.RSS = 'RSS'
