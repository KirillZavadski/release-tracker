from flask import Blueprint, render_template
from flask_login import login_required, current_user

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def main_page():
    return render_template('main_page.html', user=current_user)

@pages_bp.route('/login')
def login_page():
    return render_template('login.html')

@pages_bp.route('/register')
def register_page():
    return render_template('register.html')

@pages_bp.route('/services/<int:service_id>/releases')
@login_required
def releases_page(service_id):
    return render_template('releases.html', service_id=service_id)

@pages_bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=current_user)