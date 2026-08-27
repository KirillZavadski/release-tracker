import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from api import db_api

def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    @app.route('/')
    def index():
        return {"message": "Release Tracker API is running!"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)