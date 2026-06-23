from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime, timedelta
import secrets

# ================================================================
# ✅ تعريف Blueprint (يجب أن يكون في الأعلى)
# ================================================================
auth_bp = Blueprint('auth', __name__)

# ================================================================
# ✅ دوال المصادقة الأساسية
# ================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pages.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # ✅ استخدم check_password
            login_user(user)
            user.online = True
            db.session.commit()
            return redirect(url_for('pages.index'))
        else:
            return render_template('login.html', error='❌ اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pages.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='❌ اسم المستخدم موجود')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='❌ البريد الإلكتروني موجود')
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            avatar=f'https://i.pravatar.cc/150?img={User.query.count() + 10}'
        )
        user.set_password(password)  # ✅ تشفير كلمة المرور
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('pages.index'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    current_user.online = False
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

# ================================================================
# ✅ دوال إعادة تعيين كلمة المرور (Forgot Password)
# ================================================================
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('❌ البريد الإلكتروني غير مسجل', 'danger')
            return render_template('forgot_password.html', user=current_user)

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

        reset_link = url_for('auth.reset_password', token=token, _external=True)

        # ✅ إرسال البريد الإلكتروني مع طباعة الأخطاء
        try:
            from flask_mail import Message
            from app import mail  # استيراد mail من app.py

            msg = Message(
                subject='🔑 إعادة تعيين كلمة المرور - Socialite',
                recipients=[email],
                body=f'''
مرحباً،

لقد طلبت إعادة تعيين كلمة المرور لحسابك في Socialite.

اضغط على الرابط التالي لإعادة تعيين كلمة المرور (صالح لمدة 15 دقيقة):

{reset_link}

إذا لم تطلب ذلك، يمكنك تجاهل هذه الرسالة.

مع تحيات فريق Socialite
'''
            )
            mail.send(msg)
            print(f'✅ تم إرسال البريد إلى: {email}')
            flash('✅ تم إرسال رابط إعادة التعيين إلى بريدك', 'success')

        except Exception as e:
            print(f'❌ فشل إرسال البريد: {e}')
            flash(f'❌ حدث خطأ في إرسال البريد: {str(e)}', 'danger')
            return render_template('forgot_password.html', user=current_user)

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', user=current_user)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('❌ الرابط غير صالح أو منتهي الصلاحية', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('✅ تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token, user=current_user)
