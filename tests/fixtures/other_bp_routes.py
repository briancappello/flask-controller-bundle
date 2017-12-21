from flask_controller_bundle import func, prefix, include

from .bp_views import one, two, three


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
    include('tests.fixtures.other_bp_routes', 'explicit'),
    prefix('/deep', [
        include('tests.fixtures.other_bp_routes', attr_name='implicit')
    ]),
]
