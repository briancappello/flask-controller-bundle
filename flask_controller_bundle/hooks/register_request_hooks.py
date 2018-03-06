from flask import Flask
from flask_unchained import AppFactoryHook
from typing import *

from ..attr_constants import REQUEST_HOOK_TYPE


flask_attrs = {
    'before_request': 'before_request_funcs',
    'before_first_request': 'before_first_request_funcs',
    'after_request': '_funcs',
    'teardown_request': '_funcs',
}


class RegisterRequestHooks(AppFactoryHook):
    name = 'request_hooks'
    priority = 30

    bundle_module_name = 'request_hooks'

    action_table_columns = ['name', 'hook_type']
    action_table_converter = lambda fn: [fn.__name__,
                                         getattr(fn, REQUEST_HOOK_TYPE)]

    def process_objects(self, app: Flask, request_hooks: Dict[str, Any]):
        for fn in request_hooks.values():
            hook_type = getattr(fn, REQUEST_HOOK_TYPE)
            getattr(app, hook_type + '_funcs').setdefault(None, []).append(fn)

    def type_check(self, obj):
        return hasattr(obj, REQUEST_HOOK_TYPE)
