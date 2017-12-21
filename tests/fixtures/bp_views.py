from flask import Blueprint

from flask_controller_bundle import Controller, Resource, route


bp = Blueprint('views', __name__, url_prefix='/bp')


@route(blueprint=bp)
def simple():
    return 'simple'


@route(blueprint=bp)
def one():
    return 'one'


@route(blueprint=bp)
def two():
    return 'two'


@route(blueprint=bp, methods=['GET', 'POST'])
def three():
    return 'three'


class SiteController(Controller):
    blueprint = bp

    @route('/')
    def index(self):
        return self.render('index')

    @route
    def about(self):
        return self.render('about')

    @route
    def terms(self):
        return self.render('terms')


class ProductController(Controller):
    blueprint = bp

    @route('/')
    def index(self):
        return self.render('index')

    @route
    def good(self):
        return self.render('good')

    @route
    def better(self):
        return self.render('better')

    @route
    def best(self):
        return self.render('best')


class UserResource(Resource):
    blueprint = bp

    def index(self):
        return self.render('index')

    def create(self):
        return self.redirect('get', id=1)

    def get(self, id):
        return self.render('get', id=id)

    def put(self, id):
        return self.redirect('get', id=id)

    def patch(self, id):
        return self.redirect('get', id=id)

    def delete(self, id):
        return self.redirect('index')


class RoleResource(Resource):
    blueprint = bp

    def index(self):
        return self.render('index')

    def create(self):
        return self.redirect('get', id=1)

    def get(self, id):
        return self.render('get', id=id)

    def put(self, id):
        return self.redirect('get', id=id)

    def patch(self, id):
        return self.redirect('get', id=id)

    def delete(self, id):
        return self.redirect('index')


class AnotherResource(Resource):
    blueprint = bp
    url_prefix = 'another'

    def index(self):
        return self.render('index')

    def get(self, id):
        return self.render('get', id=id)