from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    if not getattr(current_user, 'is_admin', False):
        return jsonify({'error': 'Forbidden'}), 403
    
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users]), 200