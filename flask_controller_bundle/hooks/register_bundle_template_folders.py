from flask import Flask
from flask.helpers import _PackageBoundObject
from flask_unchained import AppFactoryHook, Bundle
from typing import List


# FIXME test template resolution order when this is used in combination with
# RegisterBlueprintsHook


# FIXME perhaps better to do something like `class BundleBlueprint(Blueprint)`?
# would prob make it easier to declare a custom blueprint in views if the user wanted.
class _FakeBlueprint(_PackageBoundObject):
    """
    The purpose of this class is to register a custom template folder and/or
    static folder with Flask. And it seems the only way to do that is to
    pretend to be a blueprint...
    """
    def __init__(self, bundle: Bundle):
        super().__init__(bundle.module_name, bundle.template_folder)
        self.name = bundle.name
        self.static_folder = bundle.static_folder
        self.static_url_prefix = bundle.static_url_prefix

    def register(self, app: Flask, options, first_registration=False):
        if self.has_static_folder:
            app.add_url_rule(f'{self.static_url_path}/<path:filename>',
                             view_func=self.send_static_file,
                             endpoint=f'{self.name}.static')

    def __repr__(self):
        return f'<BundleBlueprint "{self.name}">'


class RegisterBundleTemplateFoldersHook(AppFactoryHook):
    bundle_module_name = None
    name = 'bundle_template_folders'
    run_before = ['blueprints']

    action_category = 'template_folders'
    action_table_columns = ['name', 'folder']
    action_table_converter = lambda bp: [bp.name, bp.template_folder]

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        for bundle_ in reversed(bundles):
            for bundle in bundle_.iter_bundles(reverse=False):
                if bundle.template_folder or bundle.static_folder:
                    bp = _FakeBlueprint(bundle)
                    app.register_blueprint(bp)
                    self.log_action(bp)


# FIXME to fully replace blueprints:
# registering error handlers
# registering before/after request functions
