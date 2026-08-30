from flask import Blueprint, request, jsonify
from models import db, Service, Release

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/')
def api_index():
    return "Fuck. This is start page of api"

#routes for servises

@api_bp.route('/services', methods=['GET'])
def get_services():
    services = db.session.execute(db.select(Service)).scalars().all()
    return jsonify([service.to_dict() for service in services]), 200

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

#routes for releases

@api_bp.route('/releases', methods=['GET'])
def get_releases():
    status_filter = request.args.get('status')
    
    tmp = db.select(Release)
    
    if status_filter:
        tmp = tmp.filter_by(status=status_filter)
        
    releases = db.session.execute(tmp).scalars().all()
    return jsonify([release.to_dict() for release in releases]), 200

@api_bp.route('/services/<int:service_id>/releases', methods=['GET'])
def get_releases_by_service(service_id):
    service = db.get_or_404(Service, service_id)
    releases = [release.to_dict() for release in service.releases]
    return jsonify(releases), 200

@api_bp.route('/releases', methods=['POST'])
def create_release():
    data = request.get_json() or {}
    
    if 'service_id' not in data or 'version' not in data:
        return jsonify({'error': 'Поля service_id и version обязательны'}), 400
        
    service = db.session.get(Service, data['service_id'])
    #service = Service.query.get(data['service_id'])
    if service is None:
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
    release = db.get_or_404(Release, release_id)
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