from flask import Blueprint, request, jsonify
from app.models.models import db, Service, Release
from app.procedures.api import api_bp
from flask_login import login_required, current_user


# api_bp = Blueprint('api', __name__, url_prefix='/api')

# @api_bp.route('/')
# def api_index():
#     return "Fuck. This is start page of api"

@api_bp.route('/services', methods=['GET'])
@login_required
def get_services():
    if getattr(current_user, 'is_admin', False):
        services = Service.query.all()
    else:
        services = Service.query.filter_by(user_id=current_user.id).all()
    
    return jsonify([service.to_dict() for service in services]), 200

@api_bp.route('/releases/<int:release_id>/service', methods=['GET']) # service by release
def get_service_by_release(release_id):
    release = db.get_or_404(Release, release_id)
    return jsonify(release.service.to_dict()), 200

@api_bp.route('/services', methods=['POST']) # add service
@login_required
def create_service():
    data = request.get_json() or {}
    
    if 'name' not in data:
        return jsonify({'error': 'Поле name обязательно для заполнения'}), 400
        
    existing_service = db.session.execute(
        db.select(Service).filter_by(name=data['name'], user_id=current_user.id)
    ).scalar_one_or_none()
    
    if existing_service:
        return jsonify({'error': 'У вас уже есть сервис с таким именем'}), 400

    new_service = Service(
        name=data['name'],
        repository_url=data.get('repository_url'),
        user_id=current_user.id
    )
    
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify(new_service.to_dict()), 201

@api_bp.route('/services/<int:service_id>', methods=['PUT', 'PATCH'])
def update_service(service_id):
    service = db.get_or_404(Service, service_id)
    data = request.get_json() or {}

    if 'name' in data:
        new_name = data['name']
        if new_name != service.name:
            existing = db.session.execute(
                db.select(Service).filter_by(name=new_name)
            ).scalar_one_or_none()
            
            if existing:
                return jsonify({'error': 'Сервис с таким именем уже существует'}), 400
            
            service.name = new_name

    if 'repository_url' in data:
        service.repository_url = data['repository_url']

    db.session.commit()
    return jsonify(service.to_dict()), 200


@api_bp.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = db.get_or_404(Service, service_id)

    db.session.execute(db.delete(Release).filter_by(service_id=service_id))

    db.session.delete(service)
    db.session.commit()

    return jsonify({
        'message': f'Сервис с ID {service_id} и все его релизы успешно удалены'
    }), 200