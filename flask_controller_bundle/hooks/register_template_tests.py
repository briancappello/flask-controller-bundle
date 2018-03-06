from flask import Flask
from flask_unchained import AppFactoryHook
from typing import Any, List, Tuple

from ..attr_constants import TEMPLATE_TEST_ATTR


class RegisterTemplateTests(AppFactoryHook):
    name = 'template_tests'
    priority = 30

    bundle_module_name = 'templates.tests'

    action_category = 'template_tests'
    action_table_columns = ['name']
    action_table_converter = lambda fn: getattr(fn, TEMPLATE_TEST_ATTR)

    def process_objects(self, app: Flask, tests: List[Tuple[str, Any]]):
        for _, fn in tests:
            test_name = getattr(fn, TEMPLATE_TEST_ATTR)
            app.jinja_env.tests[test_name] = fn

    def type_check(self, obj):
        return hasattr(obj, TEMPLATE_TEST_ATTR)

    def import_bundle_module(self, bundle):
        try:
            return super().import_bundle_module(bundle)
        except ModuleNotFoundError:
            pass