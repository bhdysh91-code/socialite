import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # ✅ تحميل المتغيرات من .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2024')

    # ✅ قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/socialite.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ البريد الإلكتروني
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # ✅ رفع الملفات
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # ✅ الجلسات
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # ✅ التطبيق
    BASE_URL = 'http://localhost:5000'
    APP_NAME = 'فيسبوك'

    # ✅ الأمان
    BCRYPT_LOG_ROUNDS = 12

    # ✅ الإعدادات الإضافية
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ✅ YouTube API
YOUTUBE_API_KEY = 'AIzaSyBr7HQToOxTQKd3uFUZ2NV-AkqCQfvQNZA'
