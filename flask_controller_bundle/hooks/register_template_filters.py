from flask import Flask
from flask_unchained import AppFactoryHook
from typing import *

from ..attr_constants import TEMPLATE_FILTER_ATTR


class RegisterTemplateFilters(AppFactoryHook):
    bundle_module_name = 'templates.filters'
    bundle_override_module_name_attr = 'template_filters_module_name'
    name = 'template_filters'

    action_category = 'template_filters'
    action_table_columns = ['name']
    action_table_converter = lambda fn: getattr(fn, TEMPLATE_FILTER_ATTR)

    def process_objects(self, app: Flask, filters: Dict[str, Any]):
        for name, fn in filters.items():
            app.jinja_env.filters[name] = fn

    def key_name(self, name, obj):
        return getattr(obj, TEMPLATE_FILTER_ATTR)

    def type_check(self, obj):
        return hasattr(obj, TEMPLATE_FILTER_ATTR)

    def import_bundle_module(self, bundle):
        try:
            return super().import_bundle_module(bundle)
        except ModuleNotFoundError:
            pass
