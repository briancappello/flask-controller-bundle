from flask_controller_bundle import func, prefix, include

from .views import one, two, three


implicit = [
    func(one),
    func(two),
    func(three),
]

explicit = [
    func('/one', one),
    func('/two', two),
    func('/three', three),
]

recursive = [
    include('tests.fixtures.other_routes', attr='explicit'),
    prefix('/deep', [
        include('tests.fixtures.other_routes', attr='implicit')
    ]),
]

routes = [
    func(one),
    func(two),
    func(three),
]
