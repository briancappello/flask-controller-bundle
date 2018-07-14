from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .register_bundle_template_folders import RegisterBundleTemplateFoldersHook


class Store:
    def __init__(self):
        self.endpoints = {}
