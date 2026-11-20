from flask import Blueprint, request, jsonify, current_app
from app.models.models import db, Service, Release
from app.models.enums import Status_variable as statuses
from app.procedures.api import api_bp
from flask_login import login_required, current_user
import traceback
from datetime import datetime


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


@api_bp.route('/releases', methods=['POST'])
@login_required
def create_release():
    data = request.get_json() or {}

    if 'service_id' not in data or 'version' not in data:
        return jsonify({'error': 'Поля service_id и version обязательны'}), 400

    version = str(data['version']).strip()
    if not version:
        return jsonify({'error': 'Поле version не может быть пустым'}), 400

    service = db.session.get(Service, data['service_id'])
    if service is None:
        return jsonify({'error': 'Сервис с таким service_id не найден'}), 404

    new_release = Release(
        service_id=service.id,
        version=version,
        changelog=data.get('changelog'),
        status=statuses.DRAFT,
        deadline=None
    )

    db.session.add(new_release)
    db.session.commit()

    return jsonify(new_release.to_dict()), 201


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
    

def parse_deadline(raw_deadline) -> datetime | None: # chenge date format
    if not raw_deadline or not isinstance(raw_deadline, str):
        return None

    cleaned = raw_deadline.strip()
    formats = (
        '%d.%m.%Y %H:%M',   
        '%d.%m.%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M',  
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
    )
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

@api_bp.route('/releases/<int:release_id>/status', methods=['PATCH'])
@login_required
def update_release_status(release_id):
    if not getattr(current_user, 'is_admin', False):
        return jsonify({'error': 'Переводить релизы в другие статусы может только администратор'}), 403

    release = db.get_or_404(Release, release_id)
    data = request.get_json() or {}

    raw_status = data.get('status')
    if not raw_status:
        return jsonify({'error': 'Статус не указан'}), 400

    cleaned_status = str(raw_status).strip()

    target_status = next(
        (s for s in statuses if s.value == cleaned_status or s.value.upper() == cleaned_status.upper()),
        None
    )

    if target_status is None:
        allowed = [s.value for s in statuses]
        return jsonify({'error': f'Недопустимый статус. Разрешены: {allowed}'}), 400

    current_status = (
        release.status
        if isinstance(release.status, statuses)
        else next((s for s in statuses if s.value.upper() == str(release.status).upper()), None)
    )

    if current_status == statuses.DRAFT and target_status == statuses.DEPLOYED:
        return jsonify({'error': 'Нельзя перевести релиз из draft прямо в deployed, сначала пройдите testing'}), 400

    if target_status == statuses.TESTING:
        parsed_deadline = parse_deadline(data.get('deadline'))
        if parsed_deadline is None:
            return jsonify({
                'error': 'При переводе в тестовый статус обязательно укажите дедлайн (дата и время, например ДД.ММ.ГГГГ ЧЧ:ММ)'
            }), 400
        release.deadline = parsed_deadline
    else:
        release.deadline = None

    release.status = target_status
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