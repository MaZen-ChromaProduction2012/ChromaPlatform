import os
from flask import Flask, send_from_directory, jsonify, request
from flask_login import LoginManager
from config import Config
from models import db, User
from routes_auth import auth_bp
from routes_orders import orders_bp
from routes_admin import admin_bp
from ai_agent import SmartAIAgent

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    ai_agent = SmartAIAgent()

    @app.route('/api/chat', methods=['POST'])
    def chat_with_ai():
        data = request.get_json() or {}
        msg = data.get('message', '')
        reply = ai_agent.process_message(msg)
        return jsonify({'reply': reply})

    # Frontend Page Routes
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/login')
    def login_page():
        return send_from_directory('../frontend', 'login.html')

    @app.route('/signup')
    def signup_page():
        return send_from_directory('../frontend', 'signup.html')

    @app.route('/dashboard/client')
    def client_dashboard():
        return send_from_directory('../frontend', 'dashboard_client.html')

    @app.route('/dashboard/editor')
    def editor_dashboard():
        return send_from_directory('../frontend', 'dashboard_editor.html')

    @app.route('/dashboard/admin')
    def admin_dashboard():
        return send_from_directory('../frontend', 'dashboard_admin.html')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
