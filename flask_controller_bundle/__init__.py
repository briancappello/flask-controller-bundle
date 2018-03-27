from flask import Flask
from flask_unchained import Bundle

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, INDEX, PATCH, PUT)
from .controller import Controller
from .decorators import (
    no_route, route, template_filter, template_tag, template_test)
from .resource import Resource
from .routes import controller, func, include, prefix, resource, rule
from .utils import get_url, redirect, url_for


class FlaskControllerBundle(Bundle):
    @classmethod
    def before_init_app(cls, app: Flask):
        from .template_loader import (UnchainedJinjaEnvironment,
                                      UnchainedJinjaLoader)
        app.jinja_environment = UnchainedJinjaEnvironment
        app.jinja_options = {**app.jinja_options,
                             'loader': UnchainedJinjaLoader(app)}
