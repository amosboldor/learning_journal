"""Views for learning journal."""
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import datetime
from sqlalchemy.exc import DBAPIError
from ..models import Entry


@view_config(route_name="home", renderer="../templates/index.jinja2")
def home_list(request):
    """View for the home page."""
    try:
        query = request.dbsession.query(Entry)
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'posts': query}


@view_config(route_name="detail", renderer="../templates/post_detail.jinja2")
def detail(request):
    """View for the detail page."""
    query = request.dbsession.query(Entry)
    post_dict = query.filter(Entry.id == request.matchdict['id']).first()
    return {"post": post_dict}


@view_config(route_name="create", renderer="../templates/new_entry.jinja2")
def create(request):
    """View for new entry page."""
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        creation_date = datetime.date.today().strftime("%m/%d/%Y")
        new_model = Entry(title=title, body=body, creation_date=creation_date)
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('home'))
    return {}


@view_config(route_name="update", renderer="../templates/edit_entry.jinja2")
def update(request):
    """View for update page."""
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        creation_date = datetime.date.today().strftime("%m/%d/%Y")
        query = request.dbsession.query(Entry)
        post_dict = query.filter(Entry.id == request.matchdict['id'])
        post_dict.update({"title": title, "body": body, "creation_date": creation_date})
        return HTTPFound(location=request.route_url('home'))
    query = request.dbsession.query(Entry)
    post_dict = query.filter(Entry.id == request.matchdict['id']).first()
    return {"post": post_dict}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
