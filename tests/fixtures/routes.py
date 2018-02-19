from flask_controller_bundle import func, controller, resource, prefix, include

from .views import (SiteController, ProductController, simple,
                    UserResource, RoleResource, AnotherResource)


explicit_routes = [
    controller('/', SiteController),
    resource('/users', UserResource, subresources=[
        resource('/roles', RoleResource),
    ]),
    controller('/products', ProductController),
    func('/simple', simple),
    include('tests.fixtures.other_routes', attr_name='explicit'),
]

implicit_routes = [
    controller(SiteController),
    resource(UserResource, subresources=[
        resource(RoleResource),
    ]),
    controller(ProductController),
    func(simple),
    include('tests.fixtures.other_routes', attr_name='implicit'),
]

deep = [
    prefix('/app', [
        controller('/site', SiteController),
        prefix('/pre', [
            resource(UserResource, subresources=[
                resource(RoleResource, subresources=[
                    # this deep of nesting is probably a bad idea,
                    # but it should work regardless
                    func(simple),
                    resource(AnotherResource),
                    include('tests.fixtures.other_routes', attr_name='recursive'),
                ]),
            ]),
        ]),
    ]),
]
