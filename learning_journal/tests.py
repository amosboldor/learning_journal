"""A short testing suite for the expense tracker."""


import pytest
import transaction

from pyramid import testing

from .models import Entry, get_tm_session
from .models.meta import Base
from .scripts.initializedb import ENTRIES
import datetime


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
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
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

# ======== FUNCTIONAL TESTS ===========


# @pytest.fixture
# def testapp():
#     """Create an instance of webtests TestApp for testing routes.

#     With the alchemy scaffold we need to add to our test application the
#     setting for a database to be used for the models.
#     We have to then set up the database by starting a database session.
#     Finally we have to create all of the necessary tables that our app
#     normally uses to function.

#     The scope of the fixture is function-level, so every test will get a new
#     test application.
#     """
#     from webtest import TestApp
#     from learing_journal import main

#     app = main({}, **{"sqlalchemy.url": 'sqlite:///:memory:'})
#     testapp = TestApp(app)

#     SessionFactory = app.registry["dbsession_factory"]
#     engine = SessionFactory().bind
#     Base.metadata.create_all(bind=engine)

#     return testapp


# @pytest.fixture
# def fill_the_db(testapp):
#     """Fill the database with some model instances.

#     Start a database session with the transaction manager and add all of the
#     expenses. This will be done anew for every test.
#     """
#     SessionFactory = testapp.app.registry["dbsession_factory"]
#     with transaction.manager:
#         dbsession = get_tm_session(SessionFactory, transaction.manager)
#         dbsession.add_all(STUFF)


# def test_home_route_has_table(testapp):
#     """The home page has a table in the html."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     import pdb; pdb.set_trace()
#     assert len(html.find_all("table")) == 1


# def test_home_route_with_data_has_filled_table(testapp, fill_the_db):
#     """When there's data in the database, the home page has some rows."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 101


# def test_home_route_has_table2(testapp):
#     """Without data the home page only has the header row in its table."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 1
