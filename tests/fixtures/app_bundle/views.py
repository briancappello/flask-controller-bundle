from flask import Blueprint

from flask_controller_bundle import route


one = Blueprint('one', __name__)
two = Blueprint('two', __name__, url_prefix='/two')


@route(blueprint=one)
def view_one():
    return 'view_one'


@route(blueprint=two)
def view_two():
    return 'view_two'
