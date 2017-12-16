from flask_unchained import Bundle

from .controller import Controller
from .decorators import route
from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .resource import Resource
from .routes import controller, func, include, prefix, resource


class FlaskControllerBundle(Bundle):
    hooks = [RegisterBlueprintsHook, RegisterRoutesHook]
