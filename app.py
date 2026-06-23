from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from models import db, User
from routes import register_routes

# ✅ تعريف التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-2024'

# ✅ إعدادات قاعدة البيانات
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'socialite.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ ✅ ✅ إعدادات البريد الإلكتروني (Flask-Mail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bhdysh91@gmail.com'
app.config['MAIL_PASSWORD'] = 'nkzawwfwzguurlwv'  # ✅ كلمة مرور التطبيق (بدون مسافات)
app.config['MAIL_DEFAULT_SENDER'] = 'bhdysh91@gmail.com'

# ✅ تهيئة البريد
mail = Mail(app)

# ✅ إنشاء مجلد instance إن لم يكن موجوداً
os.makedirs(os.path.dirname(db_path), exist_ok=True)

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
        # ✅ إنشاء مستخدمين افتراضيين (إذا كانت قاعدة البيانات فارغة)
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
    app.run(host='0.0.0.0', port=5000, debug=True)
