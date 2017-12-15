from .attr_constants import ROUTE_ATTR
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          member=False, methods=None, **rule_options):
    def wrapper(fn):
        route = Route(rule, fn, blueprint=blueprint, defaults=defaults,
                      endpoint=endpoint, is_member=member, methods=methods,
                      **rule_options)
        setattr(fn, ROUTE_ATTR, route)
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper
