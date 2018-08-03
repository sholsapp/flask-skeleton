"""A custom API blueprint.

This api module is *additional* to the CRUD API exposed by Flask-Restless. It
should be used only when a custom, non-CRUD, API is necessary.

"""

from flask import Blueprint


api = Blueprint('api', __name__, template_folder='templates')


@api.route('/')
def status():
    return 'GOOD'
