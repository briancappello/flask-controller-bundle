import os

from flask import render_template

from .metaclasses import ControllerMeta
from .route import Route
from .utils import controller_name, de_camel, join


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
        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            return getattr(self, method_name)(*args, **kwargs)

        if cls.decorators:
            view.__name__ = method_name
            view.__module__ = cls.__module__
            for decorator in reversed(cls.decorators):
                view = decorator(view)

        cls_fn = getattr(cls, method_name)
        view.view_class = cls
        view.__doc__ = getattr(cls_fn, '__doc__', cls.__doc__) or cls.__doc__
        view.__name__ = method_name
        view.__module__ = cls.__module__
        return view

    @classmethod
    def route_rule(cls, route: Route):
        rule = route._rule
        if not rule:
            rule = f"{route.method_name.replace('_', '-')}"
        return join(cls.url_prefix, rule)

    @classmethod
    def route_endpoint(cls, route: Route):
        if route._endpoint:
            return route._endpoint
        return f'{de_camel(cls.__name__)}.{route.method_name}'
