from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'client')
    phone = data.get('phone', '')

    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400

    if role not in ['client', 'editor']:
        role = 'client'

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'message': 'اسم المستخدم أو البريد الإلكتروني مسجل بالفعل'}), 400

    user = User(username=username, email=email, role=role, phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({
        'success': True,
        'message': 'تم التسجيل بنجاح',
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    user = User.query.filter((User.username == identifier) | (User.email == identifier.lower())).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401

    if user.is_banned:
        return jsonify({'success': False, 'message': 'تم حظر هذا الحساب لتجاوزه 3 إنذارات'}), 403

    login_user(user)
    return jsonify({
        'success': True,
        'message': 'تم تسجيل الدخول بنجاح',
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    })

@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'تم تسجيل الخروج بنجاح'})

@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'warnings': current_user.warnings_count
            }
        })
    return jsonify({'authenticated': False})
