import functools
import jinja2
import markupsafe

from flask_unchained import unchained
from typing import Callable, Iterable, Optional, Union

from .attr_constants import (
    FN_ROUTES_ATTR, NO_ROUTES_ATTR,
    TEMPLATE_FILTER_ATTR, TEMPLATE_TAG_ATTR, TEMPLATE_TEST_ATTR)
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          is_member=False, methods=None, only_if=None, **rule_options):
    def wrapper(fn):
        fn_routes = getattr(fn, FN_ROUTES_ATTR, [])
        route = Route(rule, fn, blueprint=blueprint, defaults=defaults,
                      endpoint=endpoint, is_member=is_member, methods=methods,
                      only_if=only_if, **rule_options)
        setattr(fn, FN_ROUTES_ATTR, fn_routes + [route])
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper


def no_route(arg=None):
    def wrapper(fn):
        setattr(fn, NO_ROUTES_ATTR, True)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper


def template_filter(arg: Optional[Callable]=None,
                    *,
                    name: Optional[str]=None,
                    pass_context: bool=False,
                    inject: Optional[Union[bool, Iterable[str]]]=None,
                    safe: bool=False,
                    ) -> Callable:
    def wrapper(fn):
        fn = _inject(fn, inject)
        if safe:
            fn = _make_safe(fn)
        if pass_context:
            fn = jinja2.contextfilter(fn)
        setattr(fn, TEMPLATE_FILTER_ATTR, name or fn.__name__)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper


def template_tag(arg: Optional[Callable]=None,
                 *,
                 name: Optional[str]=None,
                 pass_context: bool=False,
                 inject: Optional[Union[bool, Iterable[str]]]=None,
                 safe: bool=False,
                 ) -> Callable:
    def wrapper(fn):
        fn = _inject(fn, inject)
        if safe:
            fn = _make_safe(fn)
        if pass_context:
            fn = jinja2.contextfunction(fn)
        setattr(fn, TEMPLATE_TAG_ATTR, name or fn.__name__)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper


def template_test(arg: Optional[Callable]=None,
                  *,
                  name: Optional[str]=None,
                  inject: Optional[Union[bool, Iterable[str]]]=None,
                  safe: bool=False,
                  ) -> Callable:
    def wrapper(fn):
        fn = _inject(fn, inject)
        if safe:
            fn = _make_safe(fn)
        setattr(fn, TEMPLATE_TEST_ATTR, name or fn.__name__)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper


def _inject(fn, inject_args):
    if not inject_args:
        return fn

    inject_args = inject_args if isinstance(inject_args, Iterable) else []
    return unchained.inject(*inject_args)(fn)


def _make_safe(fn):
    @functools.wraps(fn)
    def safe_fn(*args, **kwargs):
        return markupsafe.Markup(fn(*args, **kwargs))
    return safe_fn
