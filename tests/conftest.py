import os
import pytest

from collections import namedtuple

from flask import Flask, template_rendered


@pytest.fixture()
def app():
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    app = Flask('tests', template_folder=template_folder)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture()
def templates(app):
    records = []
    RenderedTemplate = namedtuple('RenderedTemplate', 'template context')

    def record(sender, template, context, **extra):
        records.append(RenderedTemplate(template, context))
    template_rendered.connect(record, app)

    try:
        yield records
    finally:
        template_rendered.disconnect(record, app)
