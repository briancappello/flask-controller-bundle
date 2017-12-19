from .utils import join, method_name_to_url, snake_case


class Route:
    def __init__(self, rule, view_func, blueprint=None, defaults=None,
                 endpoint=None, is_member=False, methods=None, **rule_options):
        self._rule = rule
        self.rule_options = rule_options
        self.view_func = view_func
        self.blueprint = blueprint
        self.defaults = defaults
        self._endpoint = endpoint
        self.is_member = is_member
        self.methods = methods

        # extra private (should only be used by controller metaclasses)
        self._controller_name = None

    @property
    def bp_prefix(self):
        if not self.blueprint:
            return None
        return self.blueprint.url_prefix

    @property
    def defaults(self):
        return self.rule_options['defaults']

    @defaults.setter
    def defaults(self, defaults):
        self.rule_options['defaults'] = defaults

    @property
    def endpoint(self):
        if self._endpoint:
            return self._endpoint
        elif self._controller_name:
            return f'{snake_case(self._controller_name)}.{self.method_name}'
        return f'{self.view_func.__module__}.{self.method_name}'

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

    @property
    def method_name(self):
        return self.view_func.__name__

    @property
    def methods(self):
        return getattr(self.view_func, 'methods',
                       self.rule_options.get('methods')) or ['GET']

    @methods.setter
    def methods(self, methods):
        self.rule_options['methods'] = methods

    @property
    def rule(self):
        if self._rule:
            return self._rule
        elif self._controller_name:
            return None
        return method_name_to_url(self.method_name)

    @rule.setter
    def rule(self, rule):
        self._rule = rule

    @property
    def full_rule(self):
        if not self.rule:
            raise Exception(f'{self} is not fully initialized (missing url rule)')
        return join(self.bp_prefix, self.rule)

    def copy(self):
        new = object.__new__(Route)
        new.__dict__ = self.__dict__.copy()
        return new

    def __repr__(self):
        return f'<Route endpoint={self.endpoint}>'
