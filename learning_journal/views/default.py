from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Entry


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    try:
        query = request.dbsession.query(Entry)
        one = query.filter(Entry.title == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'learning_journal'}


@view_config(route_name="create", renderer="../templates/form.jinja2")
def create_view(request):
    import pdb; pdb.set_trace()
    if request.method == 'POST':
        # Get the form stuff
        return {}
    return {}



@view_config(route_name="home", renderer="templates/index.jinja2")
def home_list(request):
    """View for the home page."""
    return {"posts": ENTRIES}


@view_config(route_name="detail", renderer="templates/post_detail.jinja2")
def detail(request):
    """View for the detail page."""
    return {"post": ENTRIES[int(request.matchdict['id']) - 1]}


@view_config(route_name="create", renderer="templates/new_post_form.jinja2")
def create(request):
    """View for create page."""
    return 'stuff'


@view_config(route_name="update", renderer="templates/edit_entry.jinja2")
def update(request):
    """View for update page."""
    return {"post": ENTRIES[int(request.matchdict['id']) - 1]}


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
