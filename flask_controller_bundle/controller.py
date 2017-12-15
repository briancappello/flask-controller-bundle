import functools
import os

from flask import render_template

from .metaclasses import ControllerMeta
from .route import Route
from .utils import controller_name, join, method_name_to_url


class TemplateFolderDescriptor:
    def __get__(self, instance, cls):
        return controller_name(cls)


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return cls.blueprint and cls.blueprint.url_prefix or ''


class Controller(metaclass=ControllerMeta):
    __abstract__ = True

    template_folder = TemplateFolderDescriptor()
    template_extension = '.html'

    blueprint = None
    decorators = None
    url_prefix = UrlPrefixDescriptor()

    def render(self, template_name, **ctx):
        if '.' not in template_name:
            template_name = f'{template_name}{self.template_extension}'
        if self.template_folder:
            template_name = os.path.join(self.template_folder, template_name)
        return render_template(template_name, **ctx)

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        # this code, combined with apply_decorators and dispatch_request, is
        # 95% taken from Flask's View.as_view classmethod (albeit refactored)
        # differences:
        # - we pass method_name to dispatch_request, to allow for easier
        #   customization of behavior by subclasses
        # - we apply decorators later, so they get called when the view does
        # - we also apply them in reverse, so that they get applied in the
        #   logical top-to-bottom order as declared in controllers
        def view_func(*args, **kwargs):
            self = view_func.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(method_name, *args, **kwargs)

        cls_fn = getattr(cls, method_name)
        view_func.view_class = cls
        view_func.__doc__ = getattr(cls_fn, '__doc__', cls.__doc__) or cls.__doc__
        view_func.__name__ = method_name
        view_func.__module__ = cls.__module__
        return view_func

    def dispatch_request(self, method_name, *view_args, **view_kwargs):
        method = self.apply_decorators(getattr(self, method_name))
        return method(*view_args, **view_kwargs)

    def apply_decorators(self, view_func):
        if self.decorators:
            original_view_func = view_func
            for decorator in reversed(self.decorators):
                view_func = decorator(view_func)
            functools.update_wrapper(view_func, original_view_func)
        return view_func

    @classmethod
    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            rule = method_name_to_url(route.method_name)
        return join(cls.url_prefix, rule)
