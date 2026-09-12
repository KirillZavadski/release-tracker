from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/', methods=["GET"])
def health_index():
    try:
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "details": str(e)
        }), 500