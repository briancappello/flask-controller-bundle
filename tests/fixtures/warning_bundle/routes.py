from .views import silly_condition

from flask_controller_bundle import func


routes = [
    func(silly_condition),
]
