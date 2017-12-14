from flask_application_factory import Bundle

from .controller import Controller
from .decorators import route
from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .resource import Resource
from .routes import controller, func, include, prefix, resource


class FlaskControllerBundle(Bundle):
    module_name = __name__
    hooks = [RegisterBlueprintsHook, RegisterRoutesHook]
