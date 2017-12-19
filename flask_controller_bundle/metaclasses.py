from types import FunctionType

from .attr_constants import (ABSTRACT_ATTR, NO_ROUTE_ATTR, NO_ROUTES_ATTR,
                             REMOVE_SUFFIXES_ATTR, ROUTE_ATTR, ROUTES_ATTR)
from .constants import CREATE, DELETE, GET, INDEX, PATCH, PUT
from .route import Route
from .utils import controller_name, join, get_param_tuples, method_name_to_url


CONTROLLER_REMOVE_EXTRA_SUFFIXES = ['View']
RESOURCE_REMOVE_EXTRA_SUFFIXES = ['MethodView']


class ControllerMeta(type):
    index_method_map = {INDEX: ['GET'], CREATE: ['POST']}
    member_method_map = {GET: ['GET'], PATCH: ['PATCH'],
                         PUT: ['PUT'], DELETE: ['DELETE']}

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            setattr(cls, NO_ROUTES_ATTR, get_not_views(clsdict, bases))
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, CONTROLLER_REMOVE_EXTRA_SUFFIXES))
            return cls

        routes = getattr(cls, ROUTES_ATTR, {})
        not_views = deep_getattr({}, bases, NO_ROUTES_ATTR)
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

    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            rule = method_name_to_url(route.method_name)
        return join(cls.url_prefix, rule)


class ResourceMeta(ControllerMeta):
    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, RESOURCE_REMOVE_EXTRA_SUFFIXES))
        return cls

    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            found, _, is_member = cls.lookup_resource_method(route.method_name)
            rule = (found and (is_member and cls.member_param or '/')
                          or method_name_to_url(route.method_name))
        if route.is_member:
            rule = rename_parent_resource_param_name(
                cls, join(cls.member_param, rule))
        return join(cls.url_prefix, rule)

    def subresource_route_rule(cls, subresource_route: Route):
        rule = join(cls.url_prefix, cls.member_param, subresource_route.rule)
        return rename_parent_resource_param_name(cls, rule)


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
    not_views = deep_getattr({}, bases, NO_ROUTES_ATTR, [])
    return ({n for n, m in clsdict.items()
             if is_view_func(n, m)
             and not getattr(m, ROUTE_ATTR, None)}.union(not_views))


def get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([x for x in new_suffixes if x not in existing_suffixes]
            + existing_suffixes)


def is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    is_no_route = getattr(method, NO_ROUTE_ATTR, False)
    return is_function and not (is_private or is_no_route)


def rename_parent_resource_param_name(parent_cls, url_rule):
    type_, orig_name = get_param_tuples(parent_cls.member_param)[0]
    orig_param = f'<{type_}:{orig_name}>'
    renamed_param = f'<{type_}:{controller_name(parent_cls)}_{orig_name}>'
    return url_rule.replace(orig_param, renamed_param, 1)
