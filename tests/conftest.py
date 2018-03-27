import pytest

from flask_unchained import AppFactory, TEST


@pytest.fixture(autouse=True)
def app():
    app = AppFactory.create_app(TEST)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
