import re

from typing import List, Tuple

# aliases
from flask_application_factory import kebab_case, pluralize, snake_case

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
    if trailing_slash:
        return path.rstrip('/') + '/'
    return path if path == '/' else path.rstrip('/')


def method_name_to_url(method_name) -> str:
    return f"/{kebab_case(method_name)}"


def rename_parent_resource_param_name(parent_resource_cls, url_rule):
    cls = parent_resource_cls
    type_, orig_name = get_param_tuples(cls.member_param)[0]
    orig_param_name = f'<{type_}{orig_name}>'
    renamed_member_param = f'<{type_}{controller_name(cls)}_{orig_name}>'
    return url_rule.replace(orig_param_name, renamed_member_param, 1)


def right_replace(string, old, new, count=1):
    return new.join(string.rsplit(old, count))


# from Flask-RESTful
def unpack(value):
    """
    Return a three tuple of data, code, and headers
    """
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}
