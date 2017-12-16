import re

from typing import List, Tuple

# aliases
from flask_unchained import kebab_case, pluralize, right_replace, snake_case

from .attr_constants import REMOVE_SUFFIXES_ATTR


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
    return re.findall(PARAM_NAME_RE, url_rule)


def get_last_param_name(url_rule) -> str:
    match = re.search(LAST_PARAM_NAME_RE, url_rule)
    return match.group('param_name') if match else None


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
