from flask import Flask
from flask_unchained import AppFactoryHook
from typing import Any, List, Tuple

from ..attr_constants import TEMPLATE_FILTER_ATTR


class RegisterTemplateFilters(AppFactoryHook):
    name = 'template_filters'
    priority = 30

    bundle_module_name = 'templates.filters'

    action_category = 'template_filters'
    action_table_columns = ['name']
    action_table_converter = lambda fn: getattr(fn, TEMPLATE_FILTER_ATTR)

    def process_objects(self, app: Flask, filters: List[Tuple[str, Any]]):
        for _, fn in filters:
            filter_name = getattr(fn, TEMPLATE_FILTER_ATTR)
            app.jinja_env.filters[filter_name] = fn

    def type_check(self, obj):
        return hasattr(obj, TEMPLATE_FILTER_ATTR)

    def import_bundle_module(self, bundle):
        try:
            return super().import_bundle_module(bundle)
        except ModuleNotFoundError:
            pass
