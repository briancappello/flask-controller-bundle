from flask import Flask
from flask_unchained import AppFactoryHook
from typing import *

from ..attr_constants import REQUEST_HOOK_TYPE


class RegisterRequestHooks(AppFactoryHook):
    bundle_module_name = 'request_hooks'
    name = 'request_hooks'
    run_after = ['blueprints']

    action_table_columns = ['name', 'hook_type']
    action_table_converter = lambda fn: [fn.__name__,
                                         getattr(fn, REQUEST_HOOK_TYPE)]

    def process_objects(self, app: Flask, request_hooks: Dict[str, Any]):
        for fn in request_hooks.values():
            hook_type = getattr(fn, REQUEST_HOOK_TYPE)
            getattr(app, hook_type + '_funcs').setdefault(None, []).append(fn)

    def type_check(self, obj):
        return hasattr(obj, REQUEST_HOOK_TYPE)
