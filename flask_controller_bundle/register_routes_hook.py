from flask import Flask
from flask_unchained import AppFactoryHook, Bundle

from .routes import reduce_routes


class RegisterRoutesHook(AppFactoryHook):
    priority = 30
    bundle_module_name = 'routes'

    def process_objects(self, app: Flask, app_config_cls, objects):
        for route in reduce_routes(objects):
            # FIXME maybe validate routes first? (eg for duplicates?)
            # Flask doesn't complain; it will match the first route found,
            # but maybe we should at least warn the user?
            self.store.endpoints[route.endpoint] = route
            app.add_url_rule(route.full_rule,
                             endpoint=route.endpoint,
                             view_func=route.view_func,
                             **route.rule_options)

    def collect_from_bundle(self, bundle: Bundle):
        if not bundle.app_bundle:
            return []

        module = self.import_bundle_module(bundle)
        try:
            return getattr(module, 'routes')
        except AttributeError:
            module_name = getattr(bundle,
                                  self.bundle_override_module_name_attr,
                                  self.bundle_module_name)
            full_module_name = f'{bundle.module_name}.{module_name}'
            raise AttributeError(f'Could not find a variable named `routes` '
                                 f'in the {full_module_name} module!')
