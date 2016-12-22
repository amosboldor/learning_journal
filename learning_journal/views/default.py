from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from ..models import Entry

import time


@view_config(route_name="home", renderer="../templates/index.jinja2")
def home_list(request):
    """View for the home page."""
    list_posts = []
    try:
        query = request.dbsession.query(Entry)
        for item in query.filter(Entry.id).all():
            list_posts.append({'title': item.title,
                               'creation_date': item.creation_date,
                               'id': item.id})
        # import pdb; pdb.set_trace()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'posts': list_posts}


@view_config(route_name="detail", renderer="../templates/post_detail.jinja2")
def detail(request):
    """View for the detail page."""
    query = request.dbsession.query(Entry)
    post_dict = query.filter(Entry.id == request.matchdict['id']).first()
    a = {'title': post_dict.title,
         'creation_date': post_dict.creation_date,
         'body': post_dict.body,
         'id': post_dict.id
         }
    return {"post": a}


@view_config(route_name="create", renderer="../templates/new_entry.jinja2")
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        creation_date = request.POST["creation_date"]
        new_model = Entry(title=title, body=body, creation_date=creation_date)
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('home'))
    return {"data": {"name": "A New Form"}}


@view_config(route_name="update", renderer="../templates/edit_entry.jinja2")
def update(request):
    """View for update page."""
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        creation_date = request.POST["creation_date"]
        new_model = Entry(title=title, body=body, creation_date=creation_date)
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('home'))
    query = request.dbsession.query(Entry)
    post_dict = query.filter(Entry.id == request.matchdict['id']).first()
    a = {
        'title': post_dict.title,
        'creation_date': post_dict.creation_date,
        'body': post_dict.body,
    }
    return {"post": a}


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
