from flask import Flask
from flask_unchained import AppFactoryHook
from typing import Any, List, Tuple

from ..attr_constants import TEMPLATE_TAG_ATTR


class RegisterTemplateTags(AppFactoryHook):
    name = 'template_tags'
    priority = 30

    bundle_module_name = 'templates.tags'

    action_category = 'template_tags'
    action_table_columns = ['name']
    action_table_converter = lambda fn: getattr(fn, TEMPLATE_TAG_ATTR)

    def process_objects(self, app: Flask, tags: List[Tuple[str, Any]]):
        for _, fn in tags:
            tag_name = getattr(fn, TEMPLATE_TAG_ATTR)
            app.jinja_env.globals[tag_name] = fn

    def type_check(self, obj):
        return hasattr(obj, TEMPLATE_TAG_ATTR)

    def import_bundle_module(self, bundle):
        try:
            return super().import_bundle_module(bundle)
        except ModuleNotFoundError:
            pass
