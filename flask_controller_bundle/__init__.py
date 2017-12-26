from flask_unchained import Bundle

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, INDEX, PATCH, PUT)
from .controller import Controller
from .decorators import no_route, route
from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .resource import Resource
from .routes import controller, func, include, prefix, resource
from .controller_bundle_store import ControllerBundleStore


class FlaskControllerBundle(Bundle):
    hooks = [RegisterBlueprintsHook, RegisterRoutesHook]
    store = ControllerBundleStore
