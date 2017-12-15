from .utils import de_camel, method_name_to_url_slug


class Route:
    def __init__(self, rule, view_func, endpoint=None, is_member=False,
                 defaults=None, methods=None, **rule_options):
        self._rule = rule
        self.view_func = view_func
        self._endpoint = endpoint
        self.is_member = is_member
        self.rule_options = rule_options
        self.rule_options['defaults'] = defaults
        self.rule_options['methods'] = methods
        self._controller_name = None

    @property
    def rule(self):
        if self._rule:
            return self._rule
        elif self._controller_name:
            raise NotImplementedError('use ControllerClass.route_rule(route)')
        return method_name_to_url_slug(self.method_name)

    @rule.setter
    def rule(self, rule):
        self._rule = rule

    @property
    def endpoint(self):
        if self._endpoint:
            return self._endpoint
        elif self._controller_name:
            return f'{de_camel(self._controller_name)}.{self.method_name}'
        return f'{self.view_func.__module__}.{self.method_name}'

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

    @property
    def method_name(self):
        return self.view_func.__name__

    def copy(self):
        new = object.__new__(Route)
        new.__dict__ = self.__dict__.copy()
        return new

    def __repr__(self):
        return f'<Route endpoint={self.endpoint}>'
