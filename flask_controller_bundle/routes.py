import inspect

from importlib import import_module
from typing import Iterable

from .attr_constants import ROUTE_ATTR, ROUTES_ATTR
from .controller import Controller
from .resource import Resource
from .route import Route
from .utils import join


def controller(url_prefix_or_controller_cls, controller_cls=None):
    url_prefix, controller_cls = _normalize_args(
        url_prefix_or_controller_cls, controller_cls, _is_controller_cls)

    for route in getattr(controller_cls, ROUTES_ATTR).values():  # type: Route
        yield Route(join(url_prefix, controller_cls.route_rule(route)),
                    controller_cls.method_as_view(route.method_name),
                    endpoint=controller_cls.route_endpoint(route),
                    **route.rule_options)


def func(rule_or_view_func, view_func=None, endpoint=None, defaults=None,
         methods=None, strict_slashes=None, redirect_to=None, **rule_options):
    rule, view_func = _normalize_args(
        rule_or_view_func, view_func, _is_view_func)

    route = getattr(view_func, ROUTE_ATTR, None)  # type: Route
    if route:
        route = route.copy()
        if isinstance(rule_or_view_func, str):
            route.rule = rule_or_view_func
        if endpoint is not None:
            route.endpoint = endpoint
        if defaults is not None:
            route.rule_options['defaults'] = defaults
        if methods is not None:
            route.rule_options['methods'] = methods
        if strict_slashes is not None:
            route.rule_options['strict_slashes'] = strict_slashes
        if redirect_to is not None:
            route.rule_options['redirect_to'] = redirect_to
        route.rule_options.update(rule_options)
        yield route
    else:
        yield Route(rule, view_func,
                    endpoint=endpoint, defaults=defaults,
                    methods=methods, strict_slashes=strict_slashes,
                    redirect_to=redirect_to, **rule_options)


def include(module_name):
    module = import_module(module_name)
    try:
        return list(getattr(module, 'routes'))
    except AttributeError:
        raise AttributeError(f'Could not find a variable named `routes` '
                             f'in the {module_name} module!')


def prefix(url_prefix: str, children: Iterable):
    for route in _reduce_routes(children):
        route = route.copy()
        route.rule = join(url_prefix, route.rule)
        yield route


def resource(url_prefix_or_resource_cls, resource_cls=None, subresources=None):
    url_prefix, resource_cls = _normalize_args(
        url_prefix_or_resource_cls, resource_cls, _is_resource_cls)

    resource_prefix = resource_cls.resource_prefix
    if url_prefix:
        resource_cls.resource_prefix = url_prefix

    for route in getattr(resource_cls, ROUTES_ATTR).values():  # type: Route
        yield Route(resource_cls.route_rule(route),
                    resource_cls.method_as_view(route.method_name),
                    endpoint=resource_cls.route_endpoint(route),
                    **route.rule_options)

    for route in _reduce_routes(subresources):
        route = route.copy()
        route.rule = resource_cls.subresource_route_rule(route)
        yield route

    resource_cls.resource_prefix = resource_prefix


def _is_controller_cls(controller_cls, has_rule=None):
    is_controller = (inspect.isclass(controller_cls)
                     and issubclass(controller_cls, Controller))
    is_resource = is_controller and issubclass(controller_cls, Resource)
    if is_controller and not is_resource:
        return True
    elif is_resource:
        raise ValueError(f'please use the resource function to include '
                         f'{controller_cls}')

    if has_rule:
        raise ValueError('the `controller_cls` argument is required when the '
                         'first argument to controller is a url prefix')
    else:
        raise ValueError('call to controller missing rule and/or '
                         'controller_cls arguments')


def _is_resource_cls(resource_cls, has_rule=None):
    if inspect.isclass(resource_cls) and issubclass(resource_cls, Controller):
        return True

    if has_rule:
        raise ValueError('the `resource_cls` argument is required when the '
                         'first argument to resource is a url prefix')
    else:
        raise ValueError('call to resource missing rule and/or '
                         'resource_cls arguments')


def _is_view_func(view_func, has_rule=None):
    if callable(view_func):
        return True

    if has_rule:
        raise ValueError('the `view_func` argument is required when the '
                         'first argument to func is a url rule')
    else:
        raise ValueError('call to func missing rule and/or '
                         'view_func arguments')


def _normalize_args(maybe_str, maybe_none, test):
    if isinstance(maybe_str, str):
        rule = maybe_str
        if test(maybe_none, has_rule=True):
            return rule, maybe_none
    elif test(maybe_str, has_rule=False):
        return None, maybe_str
    raise NotImplementedError


def _reduce_routes(routes):
    if not routes:
        raise StopIteration

    for route in routes:
        if isinstance(route, Route):
            yield route
        else:
            yield from _reduce_routes(route)
