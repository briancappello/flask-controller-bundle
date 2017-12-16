from types import FunctionType

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
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, ControllerMeta.extra_base_class_names))
            return cls

        routes = getattr(cls, ROUTES_ATTR, {})

        for method_name, method in clsdict.items():
            if not is_view_func(method_name, method):
                continue
            route = getattr(method, ROUTE_ATTR, None)
            if not route:
                route = Route(None, method)
            route.blueprint = clsdict.get('blueprint',
                                          deep_getattr(bases, 'blueprint'))
            route._controller_name = name
            routes[method_name] = route

        setattr(cls, ROUTES_ATTR, routes)
        return cls


class ResourceMeta(ControllerMeta):
    extra_base_class_names = ['MethodView']

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, ResourceMeta.extra_base_class_names))
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


def get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([x for x in new_suffixes if x not in existing_suffixes]
            + existing_suffixes)


def is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    return is_function and not is_private
