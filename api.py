from flask import Blueprint, request, jsonify
from models import db, Service, Release

api_bp = Blueprint('api', __name__, url_prefix='/api')

#routes for servises

@api_bp.route('/services', methods=['GET'])
def get_services():
    """Получить список всех сервисов"""
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services]), 200

@api_bp.route('/services', methods=['POST'])
def create_service():
    """Зарегистрировать новый сервис"""
    data = request.get_json() or {}
    
    if 'name' not in data:
        return jsonify({'error': 'Поле name обязательно для заполнения'}), 400
        
    if Service.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Сервис с таким именем уже существует'}), 400

    new_service = Service(
        name=data['name'],
        repository_url=data.get('repository_url')
    )
    
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify(new_service.to_dict()), 201

#routes for releases

@api_bp.route('/releases', methods=['GET'])
def get_releases():
    """Получить список релизов (с возможностью фильтрации по status)"""
    status_filter = request.args.get('status')
    
    query = Release.query
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    releases = query.all()
    return jsonify([release.to_dict() for release in releases]), 200

@api_bp.route('/releases', methods=['POST'])
def create_release():
    """Создать новый релиз для сервиса"""
    data = request.get_json() or {}
    
    if 'service_id' not in data or 'version' not in data:
        return jsonify({'error': 'Поля service_id и version обязательны'}), 400
        
    service = Service.query.get(data['service_id'])
    if not service:
        return jsonify({'error': 'Сервис с таким service_id не найден'}), 404

    new_release = Release(
        service_id=data['service_id'],
        version=data['version'],
        changelog=data.get('changelog'),
        status=data.get('status', 'draft')
    )
    
    db.session.add(new_release)
    db.session.commit()
    
    return jsonify(new_release.to_dict()), 201

@api_bp.route('/releases/<int:release_id>/status', methods=['PATCH'])
def update_release_status(release_id):
    """Обновить статус релиза с простой бизнес-логикой"""
    release = Release.query.get_or_404(release_id)
    data = request.get_json() or {}
    
    new_status = data.get('status')
    allowed_statuses = ['draft', 'testing', 'deployed']
    
    if new_status not in allowed_statuses:
        return jsonify({'error': f'Недопустимый статус. Разрешены: {allowed_statuses}'}), 400

    if release.status == 'draft' and new_status == 'deployed':
        return jsonify({'error': 'Нельзя перевести релиз из draft прямо в deployed, сначала пройдите testing'}), 400

    release.status = new_status
    db.session.commit()
    
    return jsonify(release.to_dict()), 200