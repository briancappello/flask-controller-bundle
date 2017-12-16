from types import FunctionType

from .attr_constants import (
    ABSTRACT_ATTR,
    NOT_VIEWS_ATTR,
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
            setattr(cls, NOT_VIEWS_ATTR, get_not_views(clsdict, bases))
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, ControllerMeta.extra_base_class_names))
            return cls

        routes = getattr(cls, ROUTES_ATTR, {})
        not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR)

        for method_name, method in clsdict.items():
            if (method_name in not_views
                    or not is_view_func(method_name, method)):
                continue

            route = getattr(method, ROUTE_ATTR, None)
            if not route:
                route = Route(None, method)
            route.blueprint = deep_getattr(clsdict, bases, 'blueprint')
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


def deep_getattr(clsdict, bases, name, default=sentinel):
    value = clsdict.get(name, sentinel)
    if value != sentinel:
        return value
    for base in bases:
        value = getattr(base, name, sentinel)
        if value != sentinel:
            return value
    if default != sentinel:
        return default
    raise AttributeError(name)


def get_not_views(clsdict, bases):
    not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR, [])
    return ([n for n, m in clsdict.items()
             if is_view_func(n, m)
             and n not in not_views
             and not getattr(m, ROUTE_ATTR, None)] + not_views)


def get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([x for x in new_suffixes if x not in existing_suffixes]
            + existing_suffixes)


def is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    return is_function and not is_private
