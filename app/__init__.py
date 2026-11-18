import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from app.models.models import db #, Service, Release
from app.procedures.api import api_bp
from app.error_handlers.errors_handling import errors
from app.health.health_check import health_bp
from app.procedures.pages import pages_bp
from app.procedures.users import user_bp

from .extencions import login_manager

from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = 'super-secret-key-change-it-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'pages.login_page'

    app.register_blueprint(api_bp)
    app.register_blueprint(errors)
    app.register_blueprint(health_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(user_bp)

    # @app.errorhandler(404)
    # def page_not_found(e):
    #     return jsonify(error=str(e)), 404

    @app.route('/')
    def index():
        return "message"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=3030, debug=True)