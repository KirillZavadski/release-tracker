from flask import Blueprint, request, jsonify
from app.models.models import db, Service, Release
from app.models.enums import Status_variable as statuses

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/')
def api_index():
    return "Fuck. This is start page of api"

from app.procedures import services
from app.procedures import releases