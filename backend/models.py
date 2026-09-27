from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # 'client', 'editor', 'admin'
    phone = db.Column(db.String(30), nullable=True)
    telegram_chat_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Moderation & Warnings
    warnings_count = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    
    # Relationships
    orders_created = db.relationship('Order', backref='client', lazy=True, foreign_keys='Order.client_id')
    orders_assigned = db.relationship('Order', backref='editor', lazy=True, foreign_keys='Order.editor_id')
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_warning(self):
        self.warnings_count += 1
        if self.warnings_count >= 3:
            self.is_banned = True
        return self.is_banned


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_type = db.Column(db.String(50), default='video_editing') # 'video_editing', 'color_grading', 'motion_graphics', 'reels'
    
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    status = db.Column(db.String(30), default='received') # received, downloading, rough_cut, audio_sync, color_grade, vfx, in_review, completed, cancelled
    status_text_ar = db.Column(db.String(100), default='تم استلام الطلب وبانتظار بدء العمل')
    progress_percentage = db.Column(db.Integer, default=5)
    
    uploaded_file_name = db.Column(db.String(255), nullable=True)
    uploaded_file_size = db.Column(db.String(50), nullable=True)
    delivered_file_url = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    review = db.relationship('Review', backref='order', uselist=False, lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='order', lazy=True, cascade='all, delete-orphan')


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    sender_name = db.Column(db.String(64), nullable=False)
    sender_role = db.Column(db.String(20), default='client') # 'client', 'editor', 'ai_agent'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
