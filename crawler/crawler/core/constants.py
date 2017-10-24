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

STATES.PRESERVATION_TAGS = ((
    ('PRIORITY', 'preservation:priority'),
    ('REALEASE_DATE', 'preservation:release_date'),
    ('NOT_FOUND_ONLY','preservation:notfound_only'),
))

