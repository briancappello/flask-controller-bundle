from flask_controller_bundle import Controller, include, route


routes = [
    include('tests.fixtures.vendor_bundle.routes'),
]


class SiteController(Controller):
    @route('/')
    def index(self):
        return 'index rendered'

    def about(self):
        return 'about rendered'


@route(endpoint='views.view_one')
def view_one():
    return 'view_one rendered'


@route('/two', endpoint='views.view_two')
def view_two():
    return 'view_two rendered'


def should_be_ignored():
    raise NotImplementedError
