from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook


class Store:
    def __init__(self):
        self.endpoints = {}
