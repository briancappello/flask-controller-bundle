from flask_controller_bundle import func

from .views import view_three, view_four


routes = [
    func(view_three),
    func(view_four),
]
