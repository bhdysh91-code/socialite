from flask import current_app, render_template
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import os
import secrets
from PIL import Image

mail = Mail()

def send_verification_email(user):
    """إرسال بريد توثيق الحساب"""
    token = user.generate_verification_token()
    verify_url = f"{current_app.config['BASE_URL']}/verify/{token}"
    
    msg = Message(
        subject='تأكيد البريد الإلكتروني - فيسبوك',
        recipients=[user.email],
        html=render_template('emails/verify.html', user=user, url=verify_url)
    )
    mail.send(msg)

def send_reset_password_email(user):
    """إرسال بريد إعادة تعيين كلمة المرور"""
    token = user.generate_reset_token()
    reset_url = f"{current_app.config['BASE_URL']}/reset-password/{token}"
    
    msg = Message(
        subject='إعادة تعيين كلمة المرور - فيسبوك',
        recipients=[user.email],
        html=render_template('emails/reset.html', user=user, url=reset_url)
    )
    mail.send(msg)

def save_image(file, folder, name=None):
    """حفظ الصورة مع ضغطها"""
    if not file:
        return None
    
    # إنشاء المجلد إذا لم يكن موجوداً
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # إنشاء اسم ملف فريد
    if not name:
        ext = file.filename.rsplit('.', 1)[1].lower()
        name = f"{secrets.token_hex(16)}.{ext}"
    
    # حفظ الصورة
    path = os.path.join(upload_path, name)
    file.save(path)
    
    # ضغط الصورة
    try:
        img = Image.open(path)
        img.thumbnail((800, 800))
        img.save(path, quality=85, optimize=True)
    except:
        pass
    
    return f"/static/uploads/{folder}/{name}"

def time_ago(dt):
    """تحويل الوقت إلى صيغة 'منذ'"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    
    if seconds < 60:
        return 'الآن'
    elif minutes < 60:
        return f'منذ {int(minutes)} دقيقة'
    elif hours < 24:
        return f'منذ {int(hours)} ساعة'
    elif days < 7:
        return f'منذ {int(days)} يوم'
    elif days < 30:
        return f'منذ {int(days // 7)} أسبوع'
    elif days < 365:
        return f'منذ {int(days // 30)} شهر'
    else:
        return f'منذ {int(days // 365)} سنة'

def get_friends_list(user):
    """الحصول على قائمة الأصدقاء"""
    from models import Friendship, User
    friendships = Friendship.query.filter(
        ((Friendship.user_id == user.id) | (Friendship.friend_id == user.id)),
        Friendship.status == 'accepted'
    ).all()
    
    friend_ids = []
    for f in friendships:
        if f.user_id == user.id:
            friend_ids.append(f.friend_id)
        else:
            friend_ids.append(f.user_id)
    
    return User.query.filter(User.id.in_(friend_ids)).all()

def get_mutual_friends(user1, user2):
    """الحصول على الأصدقاء المشتركين"""
    friends1 = set([f.id for f in get_friends_list(user1)])
    friends2 = set([f.id for f in get_friends_list(user2)])
    mutual = friends1.intersection(friends2)
    return User.query.filter(User.id.in_(mutual)).all()

def create_notification(user_id, type, from_user_id=None, post_id=None, message=None):
    """إنشاء إشعار جديد"""
    from models import Notification, db
    notif = Notification(
        user_id=user_id,
        type=type,
        from_user_id=from_user_id,
        post_id=post_id,
        message=message
    )
    db.session.add(notif)
    db.session.commit()
    return notif
