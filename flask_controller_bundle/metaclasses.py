from .attr_constants import (
    ABSTRACT_ATTR,
    REMOVE_SUFFIXES_ATTR,
    ROUTE_ATTR,
    ROUTES_ATTR,
)
from .route import Route


class ControllerMeta(type):
    extra_base_class_names = ['View']

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            remove_suffixes = [name] + ControllerMeta.extra_base_class_names
            setattr(cls, REMOVE_SUFFIXES_ATTR, remove_suffixes)
            return cls

        routes = getattr(cls, ROUTES_ATTR, {})

        for method_name, method in clsdict.items():
            if method_name.startswith('__') or not callable(method):
                continue
            route = getattr(method, ROUTE_ATTR, None)
            if not route:
                route = Route(None, method)
            route._controller_name = name
            routes[method_name] = route

        setattr(cls, ROUTES_ATTR, routes)
        return cls


class ResourceMeta(ControllerMeta):
    extra_base_class_names = ['MethodView']

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            remove_suffixes = ([name]
                               + ResourceMeta.extra_base_class_names
                               + deep_getattr(bases, REMOVE_SUFFIXES_ATTR))
            setattr(cls, REMOVE_SUFFIXES_ATTR, remove_suffixes)
        return cls


sentinel = object()


def deep_getattr(bases, name, default=sentinel):
    for base in bases:
        value = getattr(base, name, sentinel)
        if value != sentinel:
            return value
    if default != sentinel:
        return default
    raise AttributeError(name)
