import pytest

from flask import Blueprint

from flask_controller_bundle import Controller, Resource, route as route_
from flask_controller_bundle.attr_constants import ROUTE_ATTR, ROUTES_ATTR
from flask_controller_bundle.routes import (
    func, include, controller, resource, _normalize_args)


bp = Blueprint('test', __name__)
bp2 = Blueprint('test2', __name__)


def a_view():
    pass


@route_
def b_view():
    pass


class SiteController(Controller):
    @route_('/')
    def index(self):
        pass

    def about(self):
        pass


class UserResource(Resource):
    def index(self):
        pass

    def get(self, id):
        pass


class RoleResource(Resource):
    def index(self):
        pass

    def get(self, id):
        pass


class TestController:
    def test_it_works_with_only_a_controller_cls(self):
        routes = list(controller(SiteController))
        assert len(routes) == 2
        assert routes[0].endpoint == 'site_controller.index'
        assert routes[0].rule == '/'
        assert routes[1].endpoint == 'site_controller.about'
        assert routes[1].rule == '/about'

    def test_it_works_with_a_prefix_and_controller_cls(self):
        routes = list(controller('/prefix', SiteController))
        assert len(routes) == 2
        assert routes[0].endpoint == 'site_controller.index'
        assert routes[0].rule == '/prefix'
        assert routes[1].endpoint == 'site_controller.about'
        assert routes[1].rule == '/prefix/about'

    def test_it_requires_a_controller_cls(self):
        with pytest.raises(ValueError):
            list(controller('/fail'))

        with pytest.raises(ValueError):
            list(controller('/fail', None))

        with pytest.raises(ValueError):
            list(controller(None))

        with pytest.raises(ValueError):
            list(controller(None, SiteController))

        with pytest.raises(TypeError):
            list(controller(UserResource))

        with pytest.raises(TypeError):
            list(controller('/users', UserResource))

    def test_it_does_not_mutate_existing_routes(self):
        routes = list(controller('/prefix', SiteController))
        orig_routes = list(getattr(SiteController, ROUTES_ATTR).values())
        assert orig_routes[0].endpoint == routes[0].endpoint
        assert orig_routes[0].rule == '/'
        assert routes[0].rule == '/prefix'


class TestFunc:
    def test_it_works_with_undecorated_view(self):
        route = list(func(a_view))[0]
        assert route.view_func == a_view
        assert route.rule == '/a-view'
        assert route.blueprint is None
        assert route.endpoint == 'tests.test_routes.a_view'
        assert route.defaults is None
        assert route.methods == ['GET']
        assert route.only_if is None

    def test_override_rule_options_with_undecorated_view(self):
        route = list(func('/a/<id>', a_view, blueprint=bp,
                          endpoint='overridden.endpoint',
                          defaults={'id': 1}, methods=['GET', 'POST'],
                          only_if='only_if'))[0]
        assert route.rule == '/a/<id>'
        assert route.view_func == a_view
        assert route.blueprint == bp
        assert route.endpoint == 'overridden.endpoint'
        assert route.defaults == {'id': 1}
        assert route.methods == ['GET', 'POST']
        assert route.only_if is 'only_if'

    def test_it_works_with_decorated_view(self):
        route = list(func(b_view))[0]
        assert route.view_func == b_view
        assert route.rule == '/b-view'
        assert route.blueprint is None
        assert route.endpoint == 'tests.test_routes.b_view'
        assert route.defaults is None
        assert route.methods == ['GET']
        assert route.only_if is None

    def test_override_rule_options_with_decorated_view(self):
        route = list(func('/b/<id>', b_view, blueprint=bp,
                          endpoint='overridden.endpoint',
                          defaults={'id': 1}, methods=['GET', 'POST'],
                          only_if='only_if'))[0]
        assert route.rule == '/b/<id>'
        assert route.view_func == b_view
        assert route.blueprint == bp
        assert route.endpoint == 'overridden.endpoint'
        assert route.defaults == {'id': 1}
        assert route.methods == ['GET', 'POST']
        assert route.only_if == 'only_if'

    def test_it_requires_a_callable(self):
        with pytest.raises(ValueError):
            list(func('/fail'))

        with pytest.raises(ValueError):
            list(func('/fail', None))

        with pytest.raises(ValueError):
            list(func(None))

        with pytest.raises(ValueError):
            list(func(None, a_view))

    def test_it_does_not_mutate_existing_routes(self):
        route = list(func('/foo', b_view))[0]
        orig_route = getattr(b_view, ROUTE_ATTR)
        assert orig_route.endpoint == route.endpoint
        assert orig_route.rule == '/b-view'
        assert route.rule == '/foo'


class TestInclude:
    def test_it_raises_if_no_routes_found(self):
        with pytest.raises(ImportError):
            # trying to import this.should.fail prints the zen of python!
            list(include('should.not.exist'))

        with pytest.raises(AttributeError):
            list(include('tests.fixtures.routes'))

        with pytest.raises(AttributeError):
            list(include('tests.fixtures.routes', attr_name='fail'))

    def test_it_only_includes_only(self):
        routes = list(include('tests.fixtures.other_routes', only=['views.one']))
        assert len(routes) == 1
        assert routes[0].endpoint == 'views.one'

    def test_it_does_not_include_excludes(self):
        routes = list(include('tests.fixtures.other_routes', exclude=['views.three']))
        assert len(routes) == 2
        assert routes[0].endpoint == 'views.one'
        assert routes[1].endpoint == 'views.two'


class TestResource:
    def test_it_works_with_only_resource(self):
        routes = list(resource(UserResource))
        assert len(routes) == 2
        assert routes[0].endpoint == 'user_resource.index'
        assert routes[0].rule == '/users'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/users/<int:id>'

    def test_it_works_with_a_prefix(self):
        routes = list(resource('/prefix', UserResource))
        assert len(routes) == 2
        assert routes[0].endpoint == 'user_resource.index'
        assert routes[0].rule == '/prefix'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/prefix/<int:id>'

    def test_it_requires_a_controller(self):
        with pytest.raises(ValueError):
            list(resource('/fail'))

        with pytest.raises(ValueError):
            list(resource('/fail', None))

        with pytest.raises(ValueError):
            list(resource(None))

        with pytest.raises(ValueError):
            list(resource(None, UserResource))

    def test_it_does_not_mutate_existing_routes(self):
        routes = list(resource('/prefix', UserResource))
        orig_routes = list(getattr(UserResource, ROUTES_ATTR).values())
        assert orig_routes[0].endpoint == routes[0].endpoint
        assert orig_routes[0].rule == '/'
        assert routes[0].rule == '/prefix'

    def test_it_does_not_mutate_subresource_routes(self):
        routes = list(resource('/one', UserResource, subresources=[
            resource('/two', RoleResource)
        ]))
        orig_routes = list(getattr(RoleResource, ROUTES_ATTR).values())
        assert orig_routes[0].endpoint == routes[2].endpoint
        assert orig_routes[0].rule == '/'
        assert routes[2].rule == '/one/<int:user_id>/two'

    def test_it_warns_if_overriding_subresource_bp_with_none(self):
        class UserResource(Resource):
            blueprint = None

            def index(self):
                pass

        class RoleResource(Resource):
            blueprint = bp

            def index(self):
                pass

        with pytest.warns(None) as warnings:
            list(resource('/one', UserResource, subresources=[
                resource('/two', RoleResource)
            ]))
            msg = "overriding subresource blueprint 'test' with None"
            assert msg in str(warnings[0])

    def test_it_warns_if_overriding_subresource_bp_with_another_bp(self):
        class UserResource(Resource):
            blueprint = bp

            def index(self):
                pass

        class RoleResource(Resource):
            blueprint = bp2

            def index(self):
                pass

        with pytest.warns(None) as warnings:
            list(resource('/one', UserResource, subresources=[
                resource('/two', RoleResource)
            ]))
            msg = "overriding subresource blueprint 'test2' with 'test'"
            assert msg in str(warnings[0])


def test_normalize_args():
    def is_bp(maybe_bp, has_rule):
        return isinstance(maybe_bp, Blueprint)

    assert _normalize_args(bp, None, is_bp) == (None, bp)
    assert _normalize_args('str', bp, is_bp) == ('str', bp)

    # this use case makes no sense, but it completes coverage
    assert _normalize_args(None, 'str', lambda *args, **kw: False) is None
    assert _normalize_args('str', None, lambda *args, **kw: False) is None
