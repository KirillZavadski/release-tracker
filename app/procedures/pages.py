from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
@login_required
def main_page():
    user_services = current_user.services 
    return render_template('main_page.html', user=current_user, services=user_services)

@pages_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('pages.main_page'))
        
        flash('Wrong data', 'error')
        
    return render_template('login.html')

@pages_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('User with this login already exists', 'error')
            return render_template('register.html')

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('pages.main_page'))

    return render_template('register.html')

@pages_bp.route('/services/<int:service_id>/releases')
@login_required
def releases_page(service_id):
    return render_template('releases.html', service_id=service_id)

@pages_bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=current_user)

@pages_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.login_page'))