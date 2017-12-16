from .controller import Controller
from .metaclasses import ResourceMeta
from .route import Route
from .utils import (controller_name, join, pluralize, method_name_to_url,
                    rename_parent_resource_param_name)


class ResourceUrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return f'/{pluralize(controller_name(cls))}'


class Resource(Controller, metaclass=ResourceMeta):
    __abstract__ = True

    url_prefix = ResourceUrlPrefixDescriptor()
    member_param = '<int:id>'

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        _, view.methods, _ = cls._lookup_resource(method_name)
        return view

    @classmethod
    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            found, _, is_member = cls._lookup_resource(route.method_name)
            rule = (found and (is_member and cls.member_param or '/')
                    or method_name_to_url(route.method_name))
        if route.is_member:
            rule = rename_parent_resource_param_name(
                cls, join(cls.member_param, rule))
        return join(cls.url_prefix, rule)

    @classmethod
    def subresource_route_rule(cls, subresource_route: Route):
        rule = join(cls.url_prefix, cls.member_param, subresource_route.rule)
        return rename_parent_resource_param_name(cls, rule)

    @classmethod
    def _lookup_resource(cls, method_name):
        """returns a 3-tuple: found, http_methods, is_member"""
        if method_name in cls.index_method_map:
            return True, cls.index_method_map[method_name], False
        elif method_name in cls.member_method_map:
            return True, cls.member_method_map[method_name], True
        return False, None, False
