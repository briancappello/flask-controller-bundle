import pytest

from flask_controller_bundle import RegisterBlueprintsHook
from flask_unchained import AppConfig

from .fixtures.app_bundle import AppBundle
from .fixtures.app_bundle.views import one, two
from .fixtures.vendor_bundle import VendorBundle
from .fixtures.vendor_bundle.views import three, four
from .fixtures.warning_bundle import WarningBundle
from .fixtures.empty_bundle import EmptyBundle


hook = RegisterBlueprintsHook(None)


class TestRegisterBlueprintsHook:
    def test_type_check(self):
        assert hook.type_check(one) is True
        assert hook.type_check(None) is False
        assert hook.type_check('str') is False
        assert hook.type_check(lambda x: x) is False
        assert hook.type_check(1) is False

    def test_collect_from_bundle(self):
        # because blueprints get reversed again by process_objects, these are correct
        assert list(hook.collect_from_bundle(AppBundle)) == [two, one]
        assert list(hook.collect_from_bundle(VendorBundle)) == [four, three]
        assert list(hook.collect_from_bundle(EmptyBundle)) == []

        with pytest.warns(None) as warnings:
            assert list(hook.collect_from_bundle(WarningBundle)) == []
            assert len(warnings) == 1
            assert 'there was no blueprint named fail' in str(warnings[0])

    def test_run_hook(self, app):
        # later bundles override earlier ones
        # within bundles, earlier blueprints override later ones
        hook.run_hook(app, AppConfig, [VendorBundle, AppBundle])
        assert list(app.iter_blueprints()) == [one, two, three, four]