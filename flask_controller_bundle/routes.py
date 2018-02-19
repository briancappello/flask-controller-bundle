import importlib
import inspect
import sys

from flask import Blueprint
from typing import (Any, Callable, Dict, Generator, Iterable, List, Optional,
                    Set, Tuple, Type, Union)

from .attr_constants import CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR
from .controller import Controller
from .resource import Resource
from .route import Route
from .utils import join, method_name_to_url

Defaults = Dict[str, Any]
Endpoints = Union[List[str], Tuple[str], Set[str]]
Methods = Union[List[str], Tuple[str], Set[str]]
RouteGenerator = Iterable[Route]  # FIXME RouteGenerator = Generator[Route] (??)


_missing = object()

def missing_to_none(arg):
    return None if arg == _missing else arg


def controller(url_prefix_or_controller_cls: Union[str, Type[Controller]],
               controller_cls: Optional[Type[Controller]]=None,
               ) -> RouteGenerator:
    url_prefix, controller_cls = _normalize_args(
        url_prefix_or_controller_cls, controller_cls, _is_controller_cls)

    # FIXME this business of needing to set and then restore the class's
    # url_prefix is kinda very crap. (also applies in the resource function)
    controller_url_prefix = controller_cls.url_prefix
    if url_prefix:
        controller_cls.url_prefix = url_prefix

    routes = getattr(controller_cls, CONTROLLER_ROUTES_ATTR).values()

    yield from _normalize_controller_routes(routes, controller_cls)

    controller_cls.url_prefix = controller_url_prefix


def func(rule_or_view_func: Union[str, Callable],
         view_func: Optional[Callable]=_missing,
         blueprint: Optional[Blueprint]=_missing,
         defaults: Optional[Defaults]=_missing,
         endpoint: Optional[str]=_missing,
         methods: Optional[Methods]=_missing,
         only_if: Optional[Callable]=_missing,
         **rule_options,
         ) -> RouteGenerator:
    rule, view_func = _normalize_args(
        rule_or_view_func, view_func, _is_view_func)

    routes = getattr(view_func, FN_ROUTES_ATTR, [])
    routes_by_rule = {route.rule: route for route in routes}
    lookup_rule = (rule if isinstance(rule, str)
                   else method_name_to_url(view_func.__name__))
    existing_route = (routes[0] if len(routes) == 1
                      else routes_by_rule.get(lookup_rule, None))

    if existing_route:
        # we only want to override options if they were explicitly passed
        route = existing_route.copy()
        if isinstance(rule, str):
            route.rule = rule
        if blueprint is not _missing:
            route.blueprint = blueprint
        if endpoint is not _missing:
            route.endpoint = endpoint
        if defaults is not _missing:
            route.defaults = defaults
        if methods is not _missing:
            route.methods = methods
        if only_if is not _missing:
            route.only_if = only_if
        route.rule_options.update(rule_options)
        yield route
    else:
        yield Route(rule, view_func,
                    blueprint=missing_to_none(blueprint),
                    defaults=missing_to_none(defaults),
                    endpoint=missing_to_none(endpoint),
                    methods=missing_to_none(methods),
                    only_if=missing_to_none(only_if),
                    **rule_options)


def include(module_name: str,
            attr_name: str='routes',
            *,
            exclude: Optional[Endpoints]=None,
            only: Optional[Endpoints]=None,
            ) -> RouteGenerator:
    # because routes are generators, once they've been "drained", they can't be
    # used again. under normal end-user-app circumstances this reload probably
    # wouldn't be needed, but it's at least required for the tests to pass
    reload_needed = module_name in sys.modules
    module = importlib.import_module(module_name)
    if reload_needed:
        importlib.reload(module)

    try:
        routes = reduce_routes(getattr(module, attr_name))
    except AttributeError:
        raise AttributeError(f'Could not find a variable named `routes` '
                             f'in the {module_name} module!')

    def should_include_route(route):
        excluded = exclude and route.endpoint in exclude
        not_included = only and route.endpoint not in only
        if excluded or not_included:
            return False
        return True

    for route in routes:
        if should_include_route(route):
            yield route


def prefix(url_prefix: str,
           children: Iterable[Union[Route, RouteGenerator]],
           ) -> RouteGenerator:
    for route in reduce_routes(children):
        route = route.copy()
        route.rule = join(url_prefix, route.rule)
        yield route


def resource(url_prefix_or_resource_cls: Union[str, Type[Resource]],
             resource_cls: Optional[Type[Resource]]=None,
             *,
             subresources: Optional[Iterable[RouteGenerator]]=None,
             ) -> RouteGenerator:
    url_prefix, resource_cls = _normalize_args(
        url_prefix_or_resource_cls, resource_cls, _is_resource_cls)

    resource_url_prefix = resource_cls.url_prefix
    if url_prefix:
        resource_cls.url_prefix = url_prefix

    routes = getattr(resource_cls, CONTROLLER_ROUTES_ATTR).values()

    yield from _normalize_controller_routes(routes, resource_cls)

    for subroute in reduce_routes(subresources):  # type: Route
        subroute = subroute.copy()

        # can't have a subresource with a different blueprint than its parent
        bp_name = resource_cls.blueprint and resource_cls.blueprint.name
        if subroute.bp_name and (not bp_name or bp_name != subroute.bp_name):
            from warnings import warn
            warn(f'Warning: overriding subresource blueprint '
                 f'{subroute.bp_name!r} with {bp_name!r}')
        subroute.blueprint = resource_cls.blueprint

        subroute.rule = resource_cls.subresource_route_rule(subroute)
        yield subroute

    resource_cls.url_prefix = resource_url_prefix


def reduce_routes(routes: Iterable[Union[Route, RouteGenerator]],
                  ) -> RouteGenerator:
    if not routes:
        raise StopIteration

    for route in routes:
        if isinstance(route, Route):
            yield route
        else:
            yield from reduce_routes(route)


def _is_controller_cls(controller_cls, has_rule):
    is_controller = (inspect.isclass(controller_cls)
                     and issubclass(controller_cls, Controller))
    is_resource = is_controller and issubclass(controller_cls, Resource)
    if is_controller and not is_resource:
        return True
    elif is_resource:
        raise TypeError(f'please use the resource function to include '
                        f'{controller_cls}')

    if has_rule:
        raise ValueError('the `controller_cls` argument is required when the '
                         'first argument to controller is a url prefix')
    else:
        raise ValueError('call to controller missing rule and/or '
                         'controller_cls arguments')


def _is_resource_cls(resource_cls, has_rule):
    if inspect.isclass(resource_cls) and issubclass(resource_cls, Controller):
        return True

    if has_rule:
        raise ValueError('the `resource_cls` argument is required when the '
                         'first argument to resource is a url prefix')
    else:
        raise ValueError('call to resource missing rule and/or '
                         'resource_cls arguments')


def _is_view_func(view_func, has_rule):
    if callable(view_func):
        return True

    if has_rule:
        raise ValueError('the `view_func` argument is required when the '
                         'first argument to func is a url rule')
    else:
        raise ValueError('the `view_func` argument must be callable')


def _normalize_args(maybe_str, maybe_none, test):
    try:
        if isinstance(maybe_str, str):
            rule = maybe_str
            if test(maybe_none, has_rule=True):
                return rule, maybe_none
        elif test(maybe_str, has_rule=False):
            return None, maybe_str
    except ValueError as e:
        raise ValueError(f'{str(e)} (got {maybe_str}, {maybe_none})')


def _normalize_controller_routes(rules: Iterable[Route],
                                 controller_cls: Type[Controller],
                                 ) -> RouteGenerator:
    for route in reduce_routes(rules):
        route = route.copy()
        route.blueprint = controller_cls.blueprint
        route._controller_name = controller_cls.__name__
        route.view_func = controller_cls.method_as_view(route.method_name)
        route.rule = controller_cls.route_rule(route)
        yield route
