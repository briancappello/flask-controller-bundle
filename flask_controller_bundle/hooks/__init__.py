from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .register_template_filters import RegisterTemplateFilters
from .register_template_tags import RegisterTemplateTags
from .register_template_tests import RegisterTemplateTests


class Store:
    def __init__(self):
        self.endpoints = {}
