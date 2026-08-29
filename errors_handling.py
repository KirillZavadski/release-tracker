from flask import jsonify, Blueprint

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@errors.app_errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@errors.app_errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method Not Allowed'}), 405

@errors.app_errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

@errors.app_errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'something is missing?', 'details': str(e)}), 500