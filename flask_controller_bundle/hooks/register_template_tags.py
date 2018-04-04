from flask import Flask
from flask_unchained import AppFactoryHook
from typing import *

from ..attr_constants import TEMPLATE_TAG_ATTR


class RegisterTemplateTags(AppFactoryHook):
    bundle_module_name = 'templates.tags'
    bundle_override_module_name_attr = 'template_tags_module_name'
    name = 'template_tags'

    action_category = 'template_tags'
    action_table_columns = ['name']
    action_table_converter = lambda fn: getattr(fn, TEMPLATE_TAG_ATTR)

    def process_objects(self, app: Flask, tags: Dict[str, Any]):
        for name, fn in tags.items():
            app.jinja_env.globals[name] = fn

    def key_name(self, name, obj):
        return getattr(obj, TEMPLATE_TAG_ATTR)

    def type_check(self, obj):
        return hasattr(obj, TEMPLATE_TAG_ATTR)

    def import_bundle_module(self, bundle):
        try:
            return super().import_bundle_module(bundle)
        except ModuleNotFoundError:
            pass
