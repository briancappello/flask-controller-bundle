import re

from typing import List, Tuple
from urllib.parse import urlsplit

from flask import current_app as app, request, url_for

# aliases
from flask_unchained import kebab_case, pluralize, right_replace, snake_case

from .attr_constants import REMOVE_SUFFIXES_ATTR, ROUTES_ATTR


PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>')
LAST_PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>$')


def controller_name(cls) -> str:
    name = cls.__name__
    for suffix in getattr(cls, REMOVE_SUFFIXES_ATTR):
        if name.endswith(suffix):
            name = right_replace(name, suffix, '')
            break
    return snake_case(name)


def get_param_tuples(url_rule) -> List[Tuple[str, str]]:
    return [(t[:-1], n) for t, n in re.findall(PARAM_NAME_RE, url_rule)]


def get_last_param_name(url_rule) -> str:
    match = re.search(LAST_PARAM_NAME_RE, url_rule)
    return match.group('param_name') if match else None


def get_url(endpoint_or_url_or_config_key, _cls=None, **url_kwargs):
    """
    :param endpoint_or_url_or_config_key: variable name says it all
    :param _cls: if specified, can also pass a method name as the first argument
    :param url_kwargs: values to be passed along to flask's url_for
    :return: a url path, or None
    """
    what = endpoint_or_url_or_config_key

    # if what is a config key
    if what and what.isupper():
        what = app.config.get(what)

    # if we already have a url (or an invalid value, eg None)
    if not what or '/' in what:
        return what

    # if what is an endpoint
    try:
        return url_for(what, **url_kwargs)
    except Exception as e:
        if _cls is None:
            raise e

    # nope, maybe it's a class method name, let's try that endpoint
    routes = getattr(_cls, ROUTES_ATTR)
    route = routes.get(what)
    return url_for(route.endpoint, **url_kwargs)


def join(*args, trailing_slash=False):
    """
    Return a url path joined from the arguments

    (correctly handles blank/None arguments, and removes back-to-back slashes)
    """
    dirty_path = '/'.join(map(lambda x: x and x or '', args))
    path = re.sub(r'/+', '/', dirty_path)
    if path == '/':
        return path
    path = path.rstrip('/')
    return path if not trailing_slash else path + '/'


def method_name_to_url(method_name) -> str:
    return '/' + kebab_case(method_name)


# from flask_security.utils
def validate_redirect_url(url):
    if url is None or url.strip() == '':
        return False
    url_next = urlsplit(url)
    url_base = urlsplit(request.host_url)
    if (url_next.netloc or url_next.scheme) and \
            url_next.netloc != url_base.netloc:
        return False
    return True
