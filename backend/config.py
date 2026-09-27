import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chroma_secret_key_2026_super_secure')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "chroma_platform.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 250 * 1024 * 1024  # 250 MB
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'zip', 'rar', 'png', 'jpg', 'jpeg', 'wav', 'mp3'}
    
    # Internal API Secret for Telegram Bot & AI agent communication
    INTERNAL_API_KEY = os.environ.get('INTERNAL_API_KEY', 'chroma_internal_token_secret_8899')
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
