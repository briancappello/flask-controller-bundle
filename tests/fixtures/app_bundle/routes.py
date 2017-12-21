from flask_controller_bundle import func, include

from .views import view_one, view_two


routes = [
    func(view_one),
    func(view_two),
    include('tests.fixtures.vendor_bundle.routes'),
    include('tests.fixtures.warning_bundle.routes'),
]
