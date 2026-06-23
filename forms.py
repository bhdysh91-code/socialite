from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, EmailField, TextAreaField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User
import re

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('تذكرني')

class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(),
        Length(min=3, max=80),
        lambda form, field: not re.search(r'[^a-zA-Z0-9_]', field.data) or 
            ValidationError('يحتوي على أحرف غير مسموحة')
    ])
    email = EmailField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(),
        EqualTo('password', message='كلمة المرور غير متطابقة')
    ])
    birthday = DateField('تاريخ الميلاد', validators=[Optional()], format='%Y-%m-%d')
    gender = SelectField('الجنس', choices=[
        ('', 'اختر'),
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[Optional()])
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('اسم المستخدم موجود بالفعل')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('البريد الإلكتروني موجود بالفعل')

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField('نبذة', validators=[Length(max=500)])
    country = StringField('الدولة', validators=[Optional(), Length(max=100)])
    city = StringField('المدينة', validators=[Optional(), Length(max=100)])
    birthday = DateField('تاريخ الميلاد', validators=[Optional()], format='%Y-%m-%d')
    gender = SelectField('الجنس', choices=[
        ('', 'اختر'),
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[Optional()])

class AvatarForm(FlaskForm):
    avatar = FileField('صورة شخصية', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'الصور فقط!')
    ])

class CoverForm(FlaskForm):
    cover = FileField('صورة الغلاف', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'الصور فقط!')
    ])

class PostForm(FlaskForm):
    text = TextAreaField('نص المنشور', validators=[DataRequired(), Length(max=5000)])
    privacy = SelectField('الخصوصية', choices=[
        ('public', 'عام'),
        ('friends', 'الأصدقاء'),
        ('private', 'خاص')
    ], default='public')

class CommentForm(FlaskForm):
    text = TextAreaField('نص التعليق', validators=[DataRequired(), Length(max=1000)])

class MessageForm(FlaskForm):
    text = TextAreaField('الرسالة', validators=[DataRequired(), Length(max=2000)])

class ResetPasswordForm(FlaskForm):
    email = EmailField('البريد الإلكتروني', validators=[DataRequired(), Email()])

class NewPasswordForm(FlaskForm):
    password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(),
        EqualTo('password', message='كلمة المرور غير متطابقة')
    ])
