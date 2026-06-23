import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/facebook.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # البريد
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # رفع الملفات
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # الجلسات
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # التطبيق
    BASE_URL = 'http://localhost:5000'
    APP_NAME = 'فيسبوك'
    
    # الأمان
    BCRYPT_LOG_ROUNDS = 12
    
    # الإعدادات الإضافية
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
