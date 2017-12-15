from .attr_constants import ROUTE_ATTR
from .route import Route


def route(rule=None, endpoint=None, member=False, defaults=None, methods=None,
          **rule_options):
    def wrapper(fn):
        route = Route(rule, fn, endpoint=endpoint, is_member=member,
                      defaults=defaults, methods=methods,
                      **rule_options)
        setattr(fn, ROUTE_ATTR, route)
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper
