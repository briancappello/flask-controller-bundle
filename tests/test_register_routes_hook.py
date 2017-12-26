import pytest
from types import GeneratorType

from flask_controller_bundle import RegisterRoutesHook
from flask_controller_bundle import ControllerBundleStore
from flask_unchained.unchained_extension import UnchainedStore

from .fixtures.app_bundle import AppBundle
from .fixtures.vendor_bundle import VendorBundle
from .fixtures.empty_bundle import EmptyBundle


@pytest.fixture
def hook():
    bundle_store = ControllerBundleStore()
    unchained_store = UnchainedStore(None)
    return RegisterRoutesHook(unchained_store, bundle_store)


class TestRegisterRoutesHook:
    def test_collect_from_bundle(self, hook):
        routes = hook.collect_from_bundle(AppBundle)
        assert len(routes) == 4
        for route in routes:
            assert isinstance(route, GeneratorType)

        assert hook.collect_from_bundle(VendorBundle) == []

        with pytest.raises(AttributeError) as e:
            hook.collect_from_bundle(EmptyBundle)
            assert 'could not find a variable named `routes`' in str(e)

    def test_run_hook(self, app, hook):
        with app.test_request_context():
            hook.run_hook(app, [VendorBundle, AppBundle])

            expected = {'one.view_one': 'view_one',
                         'two.view_two': 'view_two',
                         'three.view_three': 'view_three',
                         'four.view_four': 'view_four'}

            # check endpoints added to store
            assert list(hook.store.endpoints.keys()) == list(expected.keys())
            for endpoint in expected:
                route = hook.store.endpoints[endpoint]
                assert route.view_func() == expected[endpoint]

            # check endpoints registered with app
            all_in_app = set(app.view_functions.keys())
            assert all_in_app.difference(set(expected.keys())) == {'static'}
            for endpoint in expected:
                view_func = app.view_functions[endpoint]
                assert view_func() == expected[endpoint]
