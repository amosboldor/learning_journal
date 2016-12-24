"""A short testing suite for the expense tracker."""


import pytest
import transaction

from pyramid import testing

# from .models import Entry, get_tm_session
from .models.meta import Base
from .scripts.initializedb import ENTRIES


from .models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    Entry
)


@pytest.fixture(scope="session")
def sqlengine(request):
    """Return sql engine."""
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:'
    })
    config.include(".models")
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope="function")
def new_session(sqlengine, request):
    """Return new session."""
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(new_session, method="GET"):
    """Instantiate a fake HTTP Request, complete with a database session."""
    request = testing.DummyRequest()
    request.method = method
    request.dbsession = new_session
    return request

STUFF = []
for index, dic in enumerate(ENTRIES):
    STUFF.append(Entry(title=dic["title"],
                       body=dic["body"],
                       creation_date=dic["creation_date"]))

# ======== UNIT TESTS ==========


def test_new_entrys_are_added(new_session):
    """New entries get added to the database."""
    new_session.add_all(STUFF)
    query = new_session.query(Entry).all()
    assert len(query) == len(STUFF)


def test_home_list_returns_empty_when_empty(dummy_request):
    """Test that the home list returns no objects in the expenses iterable."""
    from .views.default import home_list
    result = home_list(dummy_request)
    query_list = result["posts"][:]
    assert len(query_list) == 0


def test_home_list_returns_objects_when_exist(dummy_request, new_session):
    """Test that the home list does return objects when the DB is populated."""
    from .views.default import home_list
    model = Entry(title=ENTRIES[0]["title"],
                  body=ENTRIES[0]["body"],
                  creation_date=ENTRIES[0]["creation_date"])
    new_session.add(model)
    result = home_list(dummy_request)
    query_list = result["posts"][:]
    assert len(query_list) == 1


def test_detail_returns_entry_1(dummy_request, new_session):
    """Test that entry return entry one."""
    from .views.default import detail
    model = Entry(title=ENTRIES[0]["title"],
                  body=ENTRIES[0]["body"],
                  creation_date=ENTRIES[0]["creation_date"])
    new_session.add(model)
    dummy_request.matchdict['id'] = 1
    result = detail(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Monday Dude"
    assert query_reslts.body == "Today we got to learn about the python framework pyramid and it was not that hard to setup just tedious. We also had to implement a Deque and we imported double linked list to do this. Today was easy compared to other days"


def test_detail_returns_entry_2(dummy_request, new_session):
    """Test that entry return entry two."""
    from .views.default import detail
    model = Entry(title=ENTRIES[1]["title"],
                  body=ENTRIES[1]["body"],
                  creation_date=ENTRIES[1]["creation_date"])
    new_session.add(model)
    dummy_request.matchdict['id'] = 1
    result = detail(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Tuesday Dude"
    assert query_reslts.body == "Today I learned more about how routes work and we got to hock up the views to the routes a different way.\nI also learned how to use templates. One thing was very hard today was implementing binary heap.\nAnd one thing that bugged me was that I couldn’t run tests on my web because of some weird error.\nToday was hard but I didn't feel like I wanted to pull my hair out."


def test_update_returns_entry_1(dummy_request, new_session):
    """Test update returns entry two."""
    from .views.default import update
    model = Entry(title=ENTRIES[0]["title"],
                  body=ENTRIES[0]["body"],
                  creation_date=ENTRIES[0]["creation_date"])
    new_session.add(model)
    dummy_request.matchdict['id'] = 1
    result = update(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Monday Dude"
    assert query_reslts.body == "Today we got to learn about the python framework pyramid and it was not that hard to setup just tedious. We also had to implement a Deque and we imported double linked list to do this. Today was easy compared to other days"


def test_update_returns_entry_2(dummy_request, new_session):
    """Test update returns entry two."""
    from .views.default import update
    model = Entry(title=ENTRIES[1]["title"],
                  body=ENTRIES[1]["body"],
                  creation_date=ENTRIES[1]["creation_date"])
    new_session.add(model)
    dummy_request.matchdict['id'] = 1
    result = update(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Tuesday Dude"
    assert query_reslts.body == "Today I learned more about how routes work and we got to hock up the views to the routes a different way.\nI also learned how to use templates. One thing was very hard today was implementing binary heap.\nAnd one thing that bugged me was that I couldn’t run tests on my web because of some weird error.\nToday was hard but I didn't feel like I wanted to pull my hair out."


# ======== FUNCTIONAL TESTS ===========


@pytest.fixture
def testapp():
    """Create an instance of webtests TestApp for testing routes."""
    from webtest import TestApp
    from learning_journal import main

    app = main({}, **{"sqlalchemy.url": 'sqlite:///:memory:'})
    testapp = TestApp(app)

    session_factory = app.registry["dbsession_factory"]
    engine = session_factory().bind
    Base.metadata.create_all(bind=engine)

    return testapp


def test_home_route_does_not_have_all_lists(testapp):
    """The home page has all ul and li elements."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("li")) == 3
    assert len(html.find_all("ul")) == 3


def test_new_entry_route_has_input_and_textarea(testapp):
    """Test that new entry route has input and textarea."""
    response = testapp.get('/journal/new-entry', status=200)
    html = response.html
    assert len(html.find_all("input")) == 2
    assert len(html.find_all("textarea")) == 1


def test_update_entry_route_input_and_textarea(testapp):
    """Test that update entry route has input and textarea."""
    response = testapp.get('/journal/1/new-entry', status=200)
    html = response.html
    assert len(html.find_all("input")) == 2
    assert len(html.find_all("textarea")) == 1
