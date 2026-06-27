from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from models import db, User
from routes import register_routes
from news_feeds import start_news_scheduler  # ✅ استيراد فقط
import threading
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from backup import start_backup_scheduler  # ✅ أضف هذا مع الاستيرادات الأخرى
from config import Config

# ✅ تعريف التطبيق أولاً
app = Flask(__name__)
app.config.from_object(Config)

# ✅ ✅ ✅ تعيين سياق التطبيق (بعد تعريف app مباشرة)
#set_app_context(app)
# ✅ إعداد الجلسة
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
#app.config['SESSION_COOKIE_DOMAIN'] = '.trycloudflare.com'
#app.config['SESSION_COOKIE_SECURE'] = True
#app.config['SESSION_COOKIE_HTTPONLY'] = True
#app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

# ✅ إعدادات البريد الإلكتروني
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bhdysh91@gmail.com'
app.config['MAIL_PASSWORD'] = 'nkzawwfwzguurlwv'
app.config['MAIL_DEFAULT_SENDER'] = 'bhdysh91@gmail.com'
mail = Mail(app)

# ✅ ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ✅ إنشاء مجلد instance
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ تسجيل جميع المسارات
register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            users = [
                ('admin', 'admin@socialite.local', 'مدير النظام', 'admin123', True),
                ('ahmed', 'ahmed@example.com', 'أحمد', '123456', False),
                ('sara', 'sara@example.com', 'سارة', '123456', False),
                ('mohammed', 'mohammed@example.com', 'محمد', '123456', False),
                ('raneem', 'raneem@example.com', 'Raneem', '123456', False)
            ]
            for username, email, full_name, password, is_admin in users:
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    avatar=f'https://i.pravatar.cc/150?img={len(users)}',
                    is_admin=is_admin
                )
                user.set_password(password)
                db.session.add(user)
            db.session.commit()
            print('✅ تم إنشاء قاعدة البيانات')
            print('👑 admin / admin123')
            print('👤 أي مستخدم: 123456')

    print('\n' + '='*50)
    print('🌟 Socialite - التطبيق الجديد')
    print('='*50)
    print('🌐 http://localhost:5000')
    print('👑 admin / admin123')
    print('👤 أي مستخدم: 123456')
    print('='*50 + '\n')
    
    # ✅ تشغيل مجدول الأخبار
    # ✅ تشغيل مجدول النسخ الاحتياطي
    threading.Thread(target=start_backup_scheduler, daemon=True).start()
    threading.Thread(target=start_news_scheduler, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
