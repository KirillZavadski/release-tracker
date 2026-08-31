import os
from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from models import db

from api import api_bp
from errors_handling import errors
from health.health_check import health_bp

def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(api_bp)
    app.register_blueprint(errors)
    app.register_blueprint(health_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(error=str(e)), 404

    @app.route('/')
    def index():
        return "message"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=3030, debug=True)

