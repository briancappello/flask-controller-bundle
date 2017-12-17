from .controller import Controller
from .metaclasses import ResourceMeta
from .utils import controller_name, pluralize


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return '/' + pluralize(controller_name(cls))


class Resource(Controller, metaclass=ResourceMeta):
    __abstract__ = True

    url_prefix = UrlPrefixDescriptor()
    member_param = '<int:id>'

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        _, view.methods, _ = cls.lookup_resource_method(method_name)
        return view

    @classmethod
    def lookup_resource_method(cls, method_name):
        """returns a 3-tuple: found, http_methods, is_member"""
        if method_name in cls.index_method_map:
            return True, cls.index_method_map[method_name], False
        elif method_name in cls.member_method_map:
            return True, cls.member_method_map[method_name], True
        return False, None, False
