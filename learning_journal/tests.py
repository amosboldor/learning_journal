"""A testing suite for my learning journal app."""

import pytest
import transaction
from pyramid import testing
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
    assert query_reslts.title == ENTRIES[0]["title"]
    assert query_reslts.body == ENTRIES[0]["body"]


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
    assert query_reslts.title == ENTRIES[1]["title"]
    assert query_reslts.body == ENTRIES[1]["body"]


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
    assert query_reslts.title == ENTRIES[0]["title"]
    assert query_reslts.body == ENTRIES[0]["body"]


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
    assert query_reslts.title == ENTRIES[1]["title"]
    assert query_reslts.body == ENTRIES[1]["body"]


def test_update_returns_entry_random(dummy_request, new_session):
    """Test update returns entry random."""
    from .views.default import update
    model = Entry(title="WAT",
                  body="Bob Dole",
                  creation_date="1/2/3")
    new_session.add(model)
    dummy_request.matchdict['id'] = 1
    result = update(dummy_request)
    query_reslts = result["post"]
    assert query_reslts.title == "WAT"
    assert query_reslts.body == "Bob Dole"

# # ======== FUNCTIONAL TESTS ===========


@pytest.fixture
def testapp():
    """Create an instance of webtests TestApp for testing routes."""
    from webtest import TestApp
    from learning_journal import main

    app = main({}, **{'sqlalchemy.url': 'postgres:///amosboldor'})
    testapp = TestApp(app)

    session_factory = app.registry["dbsession_factory"]
    engine = session_factory().bind
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Fill the database with some model instances."""
    session_factory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for entry in ENTRIES:
            row = Entry(title=entry["title"],
                        creation_date=entry["creation_date"],
                        body=entry["body"])
            dbsession.add(row)


def test_home_route_does_not_have_all_lists(testapp):
    """The home page has all html elements from index template."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("main")) == 1
    assert len(html.find_all("ul")) == 3


def test_home_route_has_entrys(testapp, fill_the_db):
    """Test that the home page has all listed entries."""
    response = testapp.get('/', status=200)
    html = response.html
    assert html.find_all('li')[2].a.getText() == "It's Monday Dude"
    assert html.find_all('li')[3].a.getText() == "It's Tuesday Dude"


# def test_new_entry_route_has_input_and_textarea(testapp):
#     """Test that new entry route has input and textarea."""
#     response = testapp.get('/journal/new-entry', status=200)
#     html = response.html
#     assert len(html.find_all("input")) == 2
#     assert len(html.find_all("textarea")) == 1


# def test_new_entry_route_creates_new_entry_in_db(testapp):
#     """Test that new entry route creates new entry in db."""
#     title = {
#         'title': 'I have a dream.',
#         'body': 'sup'
#     }
#     response = testapp.post('/journal/new-entry', title, status=302)
#     full_response = response.follow().html.find(class_='container')
#     assert full_response.li.a.text == title["title"]


# def test_update_entry_route_input_and_textarea(testapp):
#     """Test that update entry route has input and textarea."""
#     response = testapp.get('/journal/1/edit-entry', status=200)
#     html = response.html
#     assert len(html.find_all("input")) == 2
#     assert len(html.find_all("textarea")) == 1


# def test_update_entry_route_populates_with_correct_entry(testapp, fill_the_db):
#     """Test that update entry route populates the input and textarea."""
#     response = testapp.get('/journal/1/edit-entry', status=200)
#     title = response.html.form.input["value"]
#     body = response.html.form.textarea.contents[0]
#     assert title == ENTRIES[0]["title"]
#     assert body == ENTRIES[0]["body"]


# def test_update_entry_route_update_entry(testapp, fill_the_db):
#     """Test the update view and changes title."""
#     title = {
#         'title': 'I have a dream.',
#         'body': 'sup'
#     }
#     response = testapp.post('/journal/2/edit-entry', title, status=302)
#     full_response = response.follow().html.find_all(href='http://localhost/journal/2')[0]
#     assert full_response.text == title["title"]


# def test_individual_entry_route(testapp):
#     """Test that an individual entry route brings up post_detail template."""
#     response = testapp.get('/journal/1', status=200)
#     html = response.html
#     assert len(html.find_all("main")) == 1
#     assert len(html.find_all("button")) == 2


def test_detail_route_loads_correct_entry(testapp, fill_the_db):
    """Test that the detail route loads the correct entry."""
    response = testapp.get('/journal/2', status=200)
    title = response.html.find_all(class_='container')[0].h1.getText()
    body = response.html.find_all(class_='container')[0].p.getText()
    assert title == ENTRIES[1]["title"]
    assert body == ENTRIES[1]["body"]


# ======== SECURITY UNIT TESTS ===========


# def test_login_view(dummy_request):
#     """Test that logging."""
#     from .views.default import login
#     dummy_request.POST['Username'] = 'amos'
#     dummy_request.POST['Password'] = 'password'
#     result = login(dummy_request)
#     import pdb; pdb.set_trace()
#     assert True


# ======== SECURITY FUNCTIONAL TESTS ===========

def test_login_create_ok(testapp):
    """Test that logging in gets you access to create."""
    testapp.post('/login', params={'Username': 'amos', 'Password': 'password'})
    resp = testapp.get('/journal/new-entry')
    assert resp.status_code == 200


def test_login_update_ok(testapp):
    """Test that logging in gets you access to edit-entry route."""
    testapp.post('/login',
                 params={'Username': 'amos',
                         'Password': 'password'})
    resp = testapp.get('/journal/1/edit-entry')
    assert resp.status_code == 200


def test_login_leads_to_home(testapp):
    """Test that after logging in it sends you to the home route."""
    resp = testapp.post('/login',
                        params={'Username': 'amos',
                                'Password': 'password'}).follow()
    assert len(resp.html.find('main').ul)


def test_login_page_has_fields(testapp):
    """Test that the login route brings up the login template."""
    html = testapp.get('/login').html
    assert len(html.find_all('input'))


def test_login_create_bad(testapp):
    """Test new-entry route with out logging in makes 403 error."""
    from webtest.app import AppError
    with pytest.raises(AppError):
        testapp.get('/journal/new-entry')


def test_login_update_bad(testapp):
    """Test edit-entry route with out logging in makes 403 error."""
    from webtest.app import AppError
    with pytest.raises(AppError):
        testapp.get('/journal/1/edit-entry')
