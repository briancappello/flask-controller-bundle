from flask import Flask
from flask_unchained import AppFactoryHook, Bundle

from ..routes import reduce_routes


class RegisterRoutesHook(AppFactoryHook):
    name = 'routes'
    priority = 30
    bundle_module_name = 'routes'

    action_category = 'routes'
    action_table_columns = ['rule', 'endpoint', 'view']
    action_table_converter = lambda route: [route.full_rule,
                                            route.endpoint,
                                            route.full_name]

    def process_objects(self, app: Flask, objects):
        for route in reduce_routes(objects):
            # FIXME maybe validate routes first? (eg for duplicates?)
            # Flask doesn't complain; it will match the first route found,
            # but maybe we should at least warn the user?
            if route.should_register(app):
                self.store.endpoints[route.endpoint] = route
                app.add_url_rule(route.full_rule,
                                 endpoint=route.endpoint,
                                 view_func=route.view_func,
                                 **route.rule_options)
                self.log_action(route)

    def collect_from_bundle(self, bundle: Bundle):
        if not bundle.app_bundle:
            return []

        module = self.import_bundle_module(bundle)
        try:
            return getattr(module, 'routes')
        except AttributeError:
            module_name = self.get_module_name(bundle)
            raise AttributeError(f'Could not find a variable named `routes` '
                                 f'in the {module_name} module!')
