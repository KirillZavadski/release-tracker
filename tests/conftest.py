import pytest
from app import create_app
from models import db

@pytest.fixture(scope="module", autouse=True)
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("table created")      #debug print
        yield app
        db.session.remove()
        db.drop_all()
        print("table removed")      #debug print

@pytest.fixture
def client(app):
    return app.test_client()