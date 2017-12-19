from flask import Blueprint, Flask
from flask_unchained import AppFactoryHook, Bundle
from warnings import warn


class RegisterBlueprintsHook(AppFactoryHook):
    priority = 25
    bundle_module_name = 'views'

    def process_objects(self, app: Flask, app_config_cls, objects):
        for blueprint in reversed(objects):
            # rstrip '/' off url_prefix because views should be declaring their
            # routes beginning with '/', and if url_prefix ends with '/', routes
            # will end up looking like '/prefix//endpoint', which is no good
            url_prefix = (blueprint.url_prefix or '').rstrip('/')
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    def collect_from_bundle(self, bundle: Bundle):
        bundle_blueprints = dict(super().collect_from_bundle(bundle))
        if not bundle_blueprints:
            return []

        blueprints = []
        for name in getattr(bundle, 'blueprint_names', [bundle.name]):
            try:
                blueprint = bundle_blueprints[name]
            except KeyError as e:
                warn(f'WARNING: Found a views module for the {bundle.name} '
                     f'bundle, but there was no blueprint named {e.args[0]} '
                     f'in it. Either create one, or customize the bundle\'s '
                     f'`blueprint_names` class attribute.')
                continue
            blueprints.append(blueprint)
        return reversed(blueprints)

    def type_check(self, obj):
        return isinstance(obj, Blueprint)
