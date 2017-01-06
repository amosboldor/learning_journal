"""Script that get entries from class learning journal site and adds to db."""

import requests
import os
import sys
import transaction
import dateutil.parser

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models.meta import Base
from pyramid.scripts.common import parse_vars
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import Entry


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    r = requests.get(os.environ.get('LEARN_URL', '')).json()
    entries = []

    for entry in r:
        entries.append({"title": entry["title"],
                        "id": entry["id"],
                        "creation_date": entry["created"],
                        "body": entry["text"]})

    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    settings["sqlalchemy.url"] = os.environ.get('DATABASE_URL',
                                                'sqlite:///:memory:')

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        titles = []
        for entry in dbsession.query(Entry).all():
            titles.append(entry.title)
        for entry in entries:
            if entry["title"] not in titles:
                yourdate = dateutil.parser.parse(entry["creation_date"])
                model = Entry(title=entry["title"],
                              body=entry["body"],
                              creation_date=yourdate.strftime("%m/%d/%Y"))
                dbsession.add(model)
