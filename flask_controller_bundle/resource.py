from .controller import Controller
from .metaclasses import ResourceMeta
from .route import Route
from .utils import (controller_name, join, pluralize, method_name_to_url,
                    rename_parent_resource_param_name)


class ResourcePrefixDescriptor:
    def __get__(self, instance, cls):
        return pluralize(controller_name(cls))


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return join(cls.blueprint and cls.blueprint.url_prefix or '',
                    cls.resource_prefix)


class Resource(Controller, metaclass=ResourceMeta):
    __abstract__ = True

    member_param = '<int:id>'
    resource_prefix = ResourcePrefixDescriptor()
    url_prefix = UrlPrefixDescriptor()

    index_method_map = {
        'index': ['GET', 'HEAD'],
        'create': ['POST'],
    }

    member_method_map = {
        'get': ['GET', 'HEAD'],
        'put': ['PUT'],
        'patch': ['PATCH'],
        'delete': ['DELETE'],
    }

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        if method_name in cls.index_method_map:
            view.methods = cls.index_method_map[method_name]
        elif method_name in cls.member_method_map:
            view.methods = cls.member_method_map[method_name]
        return view

    @classmethod
    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            if route.method_name in cls.index_method_map:
                rule = '/'
            elif route.method_name in cls.member_method_map:
                rule = cls.member_param
            else:
                rule = method_name_to_url(route.method_name)
        if route.is_member:
            rule = rename_parent_resource_param_name(
                cls, join(cls.member_param, rule))
        return join(cls.url_prefix, rule)

    @classmethod
    def subresource_route_rule(cls, subresource_route: Route):
        rule = join(cls.url_prefix, cls.member_param, subresource_route.rule)
        return rename_parent_resource_param_name(cls, rule)
