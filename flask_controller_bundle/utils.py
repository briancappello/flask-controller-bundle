import re

from flask import (
    Response,
    current_app as app,
    redirect as flask_redirect,
    request,
    url_for as flask_url_for,
)
from flask_unchained.string_utils import kebab_case, right_replace, snake_case
from typing import *
from urllib.parse import urlsplit
from werkzeug.routing import BuildError

from .attr_constants import CONTROLLER_ROUTES_ATTR, REMOVE_SUFFIXES_ATTR


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
    if not url_rule:
        return []
    return [(type_[:-1], name) for type_, name
            in re.findall(PARAM_NAME_RE, url_rule)]


def get_last_param_name(url_rule) -> Optional[str]:
    if not url_rule:
        return None
    match = re.search(LAST_PARAM_NAME_RE, url_rule)
    return match.group('param_name') if match else None


def get_url(endpoint_or_url_or_config_key: str,
            _cls: Optional[Union[object, type]] = None,
            _external_host: Optional[str] = None,
            **url_kwargs,
            ) -> Union[str, None]:
    """

    :param endpoint_or_url_or_config_key: variable name says it all
    :param _cls: if specified, can also pass a method name as the first argument
    :param _external_host: if specified, the host of an external server
        to generate urls for (eg https://example.com or localhost:8888)
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

    # check if it's a class method name, and try that endpoint
    if _cls and '.' not in what:
        controller_routes = getattr(_cls, CONTROLLER_ROUTES_ATTR)
        method_routes = controller_routes.get(what)
        try:
            return url_for(method_routes[0].endpoint,
                           _external_host=_external_host,
                           **url_kwargs)
        except (
            BuildError,  # url not found
            IndexError,  # method_routes[0] is out-of-range
            TypeError,   # method_routes is None
        ):
            pass

    # what must be an endpoint
    return url_for(what, _external_host=_external_host, **url_kwargs)


def join(*args, trailing_slash=False):
    """
    Return a url path joined from the arguments

    (correctly handles blank/None arguments, and removes back-to-back slashes)
    """
    dirty_path = '/'.join(map(lambda x: x and x or '', args))
    path = re.sub(r'/+', '/', dirty_path)
    if path in {'', '/'}:
        return '/'
    path = path.rstrip('/')
    return path if not trailing_slash else path + '/'


def method_name_to_url(method_name) -> str:
    return '/' + kebab_case(method_name).strip('-')


# modified from flask_security.utils.get_post_action_redirect
def redirect(where: Optional[str] = None,
             default: Optional[str] = None,
             override: Optional[str] = None,
             _cls: Optional[Union[object, type]] = None,
             _external_host: Optional[str] = None,
             **url_kwargs,
             ) -> Response:
    """
    An improved version of flask's redirect function

    :param where: A URL, endpoint, or config key name to redirect to
    :param default: A URL, endpoint, or config key name to redirect to if where
        is invalid
    :param override: explicitly redirect to a URL, endpoint, or config key name
        (takes precedence over the 'next' value in query strings or forms)
    :param _cls: if specified, allows a method name to be passed to where,
        default, and/or override
    :param _external_host: if specified, the host of an external server
        to generate urls for (eg https://example.com or localhost:8888)
    :param url_kwargs: values to be passed along to flask's url_for
    :return:
    """
    urls = [get_url(request.args.get('next')),
            get_url(request.form.get('next'))]

    if where:
        urls.append(get_url(where, _cls=_cls, _external_host=_external_host,
                            **url_kwargs))
    if default:
        urls.append(get_url(default, _cls=_cls, _external_host=_external_host,
                            **url_kwargs))
    if override:
        urls.insert(0, get_url(override, _cls=_cls,
                               _external_host=_external_host, **url_kwargs))

    for url in urls:
        if _validate_redirect_url(url):
            return flask_redirect(url)
    return flask_redirect('/')


def url_for(endpoint: str,
            _external_host: Optional[str] = None,
            **url_kwargs,
            ) -> Union[str, None]:
    """
    The same as flask's url_for, except this also supports building external
    urls for hosts that are different from app.config['SERVER_NAME']. One case
    where this is especially useful is for single page apps, where the frontend
    is not hosted by the same server as the backend, but the backend still needs
    to generate urls to frontend routes

    :param endpoint: the name of the endpoint
    :param _external_host: the host of an external server to generate
        urls for (eg https://example.com or localhost:8888)
    :param url_kwargs: any url parameter values needed to build the url
    :return: a url path, or None
    """
    external = bool(_external_host or url_kwargs.get('_external'))
    external_host = (_external_host
                        or app.config.get('EXTERNAL_SERVER_NAME'))
    if not external or not external_host:
        return flask_url_for(endpoint, **url_kwargs)

    if '://' not in external_host:
        external_host = f'http://{external_host}'
    url_kwargs.pop('_external')
    return external_host.rstrip('/') + flask_url_for(endpoint, **url_kwargs)


# from flask_security.utils
def _validate_redirect_url(url):
    if url is None or url.strip() == '':
        return False
    url_next = urlsplit(url)
    url_base = urlsplit(request.host_url)
    if (url_next.netloc or url_next.scheme) and \
            url_next.netloc != url_base.netloc:
        return False
    return True
