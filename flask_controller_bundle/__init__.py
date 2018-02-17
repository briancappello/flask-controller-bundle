from flask_unchained import Bundle

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, INDEX, PATCH, PUT)
from .controller import Controller
from .decorators import no_route, route
from .resource import Resource
from .routes import controller, func, include, prefix, resource


class FlaskControllerBundle(Bundle):
    pass
