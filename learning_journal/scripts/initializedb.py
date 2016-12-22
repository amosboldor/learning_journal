# encoding: utf-8
"""The script for initializing a database."""

import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import Entry

ENTRIES = [
    {
        "title": "It's Monday Dude",
        "id": 1,
        "creation_date": "Dec 20, 2016",
        "body": "Today we got to learn about the python framework pyramid and it was not that hard to setup just tedious. We also had to implement a Deque and we imported double linked list to do this. Today was easy compared to other days"
    },
    {
        "title": "It's Tuesday Dude",
        "id": 2,
        "creation_date": "Dec 21, 2016",
        "body": """Today I learned more about how routes work and we got to hock up the views to the routes a different way.
I also learned how to use templates. One thing was very hard today was implementing binary heap.
And one thing that bugged me was that I couldn’t run tests on my web because of some weird error.
Today was hard but I didn't feel like I wanted to pull my hair out."""
    }
]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for index, dic in enumerate(ENTRIES):
            model = Entry(title=dic["title"], body=dic["body"], creation_date=dic["creation_date"])
            dbsession.add(model)
