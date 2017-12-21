from .attr_constants import NO_ROUTE_ATTR, ROUTE_ATTR
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          is_member=False, methods=None, only_if=None, **rule_options):
    def wrapper(fn):
        route = Route(rule, fn, blueprint=blueprint, defaults=defaults,
                      endpoint=endpoint, is_member=is_member, methods=methods,
                      only_if=only_if, **rule_options)
        setattr(fn, ROUTE_ATTR, route)
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper


def no_route(arg=None):
    def wrapper(fn):
        setattr(fn, NO_ROUTE_ATTR, True)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper
