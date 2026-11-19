from flask import Blueprint, request, jsonify, current_app
from app.models.models import db, Service, Release
from app.models.enums import Status_variable as statuses
from app.procedures.api import api_bp
from flask_login import login_required, current_user
import traceback


# api_bp = Blueprint('api', __name__, url_prefix='/api')

# @api_bp.route('/')
# def api_index():
#     return "Fuck. This is start page of api"

@api_bp.route('/releases', methods=['GET'])
def get_releases():
    status_filter = request.args.get('status')
    
    release_data = db.select(Release)
    
    if status_filter:
        release_data = release_data.filter_by(status=status_filter)
        
    releases = db.session.execute(release_data).scalars().all()
    return jsonify([release.to_dict() for release in releases]), 200

@api_bp.route('/services/<int:service_id>/releases', methods=['GET']) # get releases by service
@login_required

def get_releases_by_service(service_id):
    try:
        if getattr(current_user, 'is_admin', False):
            service = db.session.execute(
                db.select(Service).filter_by(id=service_id)
            ).scalar_one_or_none()
        else:
            service = db.session.execute(
                db.select(Service).filter_by(id=service_id, user_id=current_user.id)
            ).scalar_one_or_none()
        
        if not service:
            return jsonify({'error': 'Сервис не найден'}), 404
            
        releases = [release.to_dict() for release in service.releases]
        return jsonify(releases), 200
        
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        
        error_msg = f"{type(e).__name__}: {str(e)}"
        return jsonify({'error': error_msg}), 500

@api_bp.route('/releases', methods=['POST'])
def create_release():
    data = request.get_json() or {}
    
    if 'service_id' not in data or 'version' not in data:
        return jsonify({'error': 'Поля service_id и version обязательны'}), 400
        
    valid_statuses = [status.value for status in statuses]

    service = db.session.get(Service, data['service_id'])
    if service is None:
        return jsonify({'error': 'Сервис с таким service_id не найден'}), 404

    new_release = Release(
        service_id=data['service_id'],
        version=data['version'],
        changelog=data.get('changelog'),
        status=data.get('status').upper()
    )
    
    db.session.add(new_release)
    db.session.commit()
    
    return jsonify(new_release.to_dict()), 201

@api_bp.route('/releases/<int:release_id>/status', methods=['PATCH'])
def update_release_status(release_id):
    release = db.get_or_404(Release, release_id)
    data = request.get_json() or {}
    
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Статус не указан'}), 400
        
    new_status_upper = str(new_status).upper()
    
    valid_statuses = ['DRAFT', 'TESTING', 'DEPLOYED']

    if new_status_upper not in valid_statuses:
        return jsonify({'error': f'Недопустимый статус. Разрешены: {valid_statuses}'}), 400

    current_status = str(release.status).upper()
    if 'DRAFT' in current_status and new_status_upper == 'DEPLOYED':
        return jsonify({'error': 'Нельзя перевести релиз из draft прямо в deployed, сначала пройдите testing'}), 400

    release.status = new_status_upper
    db.session.commit()
    
    return jsonify(release.to_dict()), 200

@api_bp.route('/releases/<int:release_id>', methods=['DELETE'])
def delete_release(release_id):
    release = db.get_or_404(Release, release_id)
    
    db.session.delete(release)
    db.session.commit()
    
    return jsonify({
        'message': f'Релиз с ID {release_id} успешно удален'
    }), 200