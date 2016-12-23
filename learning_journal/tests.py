"""A short testing suite for the expense tracker."""


import pytest
import transaction

from pyramid import testing

from .models import Entry, get_tm_session
from .models.meta import Base
from .scripts.initializedb import ENTRIES


@pytest.fixture(scope="session")
def configuration(request):
    """Set up a Configurator instance.

    This Configurator instance sets up a pointer to the location of the
        database.
    It also includes the models from your app's model package.
    Finally it tears everything down, including the in-memory SQLite database.

    This configuration will persist for the entire duration of your PyTest run.
    """
    settings = {
        'sqlalchemy.url': 'sqlite:///:memory:'}  # points to an in-memory database.
    config = testing.setUp(settings=settings)
    config.include('.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture()
def db_session(configuration, request):
    """Create a session for interacting with the test database.

    This uses the dbsession_factory on the configurator instance to create a
    new database session. It binds that session to the available engine
    and returns a new session for every call of the dummy_request object.
    """
    session_factory = configuration.registry['dbsession_factory']
    session = session_factory()
    engine = session.bind
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Instantiate a fake HTTP Request, complete with a database session.

    This is a function-level fixture, so every new request will have a
    new database session.
    """
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def add_models(dummy_request):
    """Add a bunch of model instances to the database.

    Every test that includes this fixture will add new random expenses.
    """
    dummy_request.dbsession.add_all(STUFF)


STUFF = []
for index, dic in enumerate(ENTRIES):
    STUFF.append(Entry(title=dic["title"],
                       body=dic["body"],
                       creation_date=dic["creation_date"]))

# ======== UNIT TESTS ==========


def test_new_entrys_are_added(db_session):
    """New entries get added to the database."""
    db_session.add_all(STUFF)
    query = db_session.query(Entry).all()
    assert len(query) == len(STUFF)


def test_home_list_returns_empty_when_empty(dummy_request):
    """Test that the home list returns no objects in the expenses iterable."""
    from .views.default import home_list
    result = home_list(dummy_request)
    query_list = result["posts"][:]
    assert len(query_list) == 0


def test_home_list_returns_objects_when_exist(dummy_request, add_models):
    """Test that the home list does return objects when the DB is populated."""
    from .views.default import home_list
    result = home_list(dummy_request)
    query_list = result["posts"][:]
    assert len(query_list) == 2


def test_detail_returns_entry_1(dummy_request, add_models):
    """Test that entry return entry one."""
    from .views.default import detail
    dummy_request.matchdict['id'] = 1
    result = detail(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Monday Dude"
    assert query_reslts.body == "Today we got to learn about the python framework pyramid and it was not that hard to setup just tedious. We also had to implement a Deque and we imported double linked list to do this. Today was easy compared to other days"


def test_detail_returns_entry_2(dummy_request, add_models):
    """Test that entry return entry two."""
    from .views.default import detail
    dummy_request.matchdict['id'] = 2
    result = detail(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Tuesday Dude"
    assert query_reslts.body == "Today I learned more about how routes work and we got to hock up the views to the routes a different way.\nI also learned how to use templates. One thing was very hard today was implementing binary heap.\nAnd one thing that bugged me was that I couldn’t run tests on my web because of some weird error.\nToday was hard but I didn't feel like I wanted to pull my hair out."


def test_update_returns_entry_1(dummy_request, add_models):
    """Test update returns entry two."""
    from .views.default import update
    dummy_request.matchdict['id'] = 1
    result = update(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "It's Monday Dude"
    assert query_reslts.body == "Today we got to learn about the python framework pyramid and it was not that hard to setup just tedious. We also had to implement a Deque and we imported double linked list to do this. Today was easy compared to other days"


def test_update_returns_entry_2(dummy_request, add_models):
    """Test update returns entry two."""
    from .views.default import update
    dummy_request.matchdict['id'] = 2
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


@pytest.fixture
def fill_the_db(testapp):
    """Fill the database with some model instances.

    Start a database session with the transaction manager and add all of the
    expenses. This will be done anew for every test.
    """
    session_factory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        dbsession.add_all(STUFF)


def test_home_route_has_list_of_enties(testapp):
    """The home page has only 3 list elements without the db."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("li")) == 3


def test_home_route_has_list_of_enties_in(testapp, fill_the_db):
    """The home page has 5 list elements with db."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("li")) == 5
