from flask import Blueprint, request, jsonify
from app.models.models import db, Service, Release
from app.procedures.api import api_bp


# api_bp = Blueprint('api', __name__, url_prefix='/api')

# @api_bp.route('/')
# def api_index():
#     return "Fuck. This is start page of api"

@api_bp.route('/services', methods=['GET'])
def get_services():
    services = db.session.execute(db.select(Service)).scalars().all()
    return jsonify([service.to_dict() for service in services]), 200

@api_bp.route('/releases/<int:release_id>/service', methods=['GET'])
def get_service_by_release(release_id):
    release = db.get_or_404(Release, release_id)
    return jsonify(release.service.to_dict()), 200

@api_bp.route('/services', methods=['POST'])
def create_service():
    data = request.get_json() or {}
    
    if 'name' not in data:
        return jsonify({'error': 'Поле name обязательно для заполнения'}), 400
        
    if db.session.execute(db.select(Service).filter_by(name=data['name'])).scalar_one_or_none():
        return jsonify({'error': 'Сервис с таким именем уже существует'}), 400

    new_service = Service(
        name=data['name'],
        repository_url=data.get('repository_url')
    )
    
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify(new_service.to_dict()), 201