from flask_controller_bundle import Resource, route
from flask_controller_bundle.attr_constants import ROUTES_ATTR
from flask_controller_bundle.constants import ALL_METHODS


class DefaultResource(Resource):
    def index(self):
        pass

    def create(self):
        pass

    def get(self):
        pass

    def patch(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def extra(self):
        pass


class TestResource:
    def test_default_attributes(self):
        assert DefaultResource.url_prefix == '/defaults'
        assert DefaultResource.member_param == '<int:id>'

    def test_custom_attributes(self):
        class FooResource(Resource):
            url_prefix = '/foobars'
            member_param = '<string:slug>'

        assert FooResource.url_prefix == '/foobars'
        assert FooResource.member_param == '<string:slug>'

    def test_method_as_view_assigns_correct_http_methods(self):
        for method_name in ALL_METHODS:
            view = DefaultResource.method_as_view(method_name)
            assert view.methods == DefaultResource.resource_methods[method_name]

        index = DefaultResource.method_as_view('index')
        assert index.methods == ['GET']

        create = DefaultResource.method_as_view('create')
        assert create.methods == ['POST']

        get = DefaultResource.method_as_view('get')
        assert get.methods == ['GET']

        patch = DefaultResource.method_as_view('patch')
        assert patch.methods == ['PATCH']

        put = DefaultResource.method_as_view('put')
        assert put.methods == ['PUT']

        delete = DefaultResource.method_as_view('delete')
        assert delete.methods == ['DELETE']

    def test_redirect_to_controller_method(self, app):
        class UserController(Resource):
            def create(self):
                return self.redirect('get', id=1)

            def get(self, id):
                pass

        with app.test_request_context():
            for method_name, route in getattr(UserController, ROUTES_ATTR).items():
                app.add_url_rule(UserController.route_rule(route),
                                 view_func=UserController.method_as_view(method_name),
                                 endpoint=route.endpoint)

            controller = UserController()
            resp = controller.create()
            assert resp.status_code == 302
            assert resp.location == '/users/1'

    def test_it_adds_route_to_extra_view_methods(self):
        routes = getattr(DefaultResource, ROUTES_ATTR)
        assert 'extra' in routes

    def test_route_rule(self):
        class FooResource(Resource):
            def a(self):
                pass

            @route(is_member=True)
            def b(self):
                pass

        routes = getattr(FooResource, ROUTES_ATTR)
        assert FooResource.route_rule(routes['a']) == '/foos/a'
        assert FooResource.route_rule(routes['b']) == '/foos/<int:foo_id>/b'

    def test_route_rule_with_resource_methods(self):
        routes = getattr(DefaultResource, ROUTES_ATTR)
        assert DefaultResource.route_rule(routes['index']) == '/defaults'
        assert DefaultResource.route_rule(routes['create']) == '/defaults'
        assert DefaultResource.route_rule(routes['get']) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['patch']) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['put']) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['delete']) == '/defaults/<int:id>'
