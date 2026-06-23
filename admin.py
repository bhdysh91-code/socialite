from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Post, Comment, Like, VerificationRequest, BanLog
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def admin_required():
    """التحقق من صلاحيات المالك"""
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'error': 'غير مصرح لك بالدخول'}), 403

@admin_bp.route('/')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    stats = {
        'users': User.query.count(),
        'posts': Post.query.count(),
        'comments': Comment.query.count(),
        'likes': Like.query.count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'verified_users': User.query.filter_by(verified=True).count(),
        'verification_requests': VerificationRequest.query.filter_by(status='pending').count()
    }
    
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin.html', stats=stats, recent_posts=recent_posts, recent_users=recent_users)

@admin_bp.route('/users')
@login_required
def users():
    """إدارة المستخدمين"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@login_required
def ban_user(user_id):
    """حظر مستخدم"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'error': 'لا يمكن حظر المالك'}), 400
    
    data = request.get_json()
    user.is_banned = True
    user.ban_reason = data.get('reason', 'تم الحظر بواسطة الإدارة')
    user.banned_at = datetime.utcnow()
    user.banned_by = current_user.id
    
    # تسجيل الحظر
    ban_log = BanLog(
        user_id=user_id,
        admin_id=current_user.id,
        action='ban',
        reason=user.ban_reason
    )
    db.session.add(ban_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'تم حظر المستخدم {user.full_name}'})

@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@login_required
def unban_user(user_id):
    """إلغاء حظر مستخدم"""
    user = User.query.get_or_404(user_id)
    
    user.is_banned = False
    user.ban_reason = None
    user.banned_at = None
    user.banned_by = None
    
    # تسجيل إلغاء الحظر
    ban_log = BanLog(
        user_id=user_id,
        admin_id=current_user.id,
        action='unban',
        reason='تم إلغاء الحظر بواسطة الإدارة'
    )
    db.session.add(ban_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'تم إلغاء حظر المستخدم {user.full_name}'})

@admin_bp.route('/verification')
@login_required
def verification_requests():
    """طلبات التوثيق"""
    requests = VerificationRequest.query.order_by(VerificationRequest.created_at.desc()).all()
    return render_template('admin_verification.html', requests=requests)

@admin_bp.route('/verification/<int:request_id>/review', methods=['POST'])
@login_required
def review_verification(request_id):
    """مراجعة طلب توثيق"""
    verification_request = VerificationRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    status = data.get('status')
    reason = data.get('reason')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'حالة غير صالحة'}), 400
    
    verification_request.status = status
    verification_request.reason = reason
    verification_request.reviewed_by = current_user.id
    verification_request.reviewed_at = datetime.utcnow()
    
    if status == 'approved':
        user = User.query.get(verification_request.user_id)
        user.verified = True
        user.verified_at = datetime.utcnow()
        user.verified_by = current_user.id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'تم ${"قبول" if status == "approved" else "رفض"} طلب التوثيق'
    })

@admin_bp.route('/domains')
@login_required
def domains():
    """إدارة الدومينات"""
    from models import Domain
    domains = Domain.query.all()
    return render_template('admin_domains.html', domains=domains)

@admin_bp.route('/domains/add', methods=['POST'])
@login_required
def add_domain():
    """إضافة دومين جديد"""
    from models import Domain
    data = request.get_json()
    
    domain = data.get('domain')
    subdomain = data.get('subdomain')
    
    if not domain:
        return jsonify({'error': 'الدومين مطلوب'}), 400
    
    new_domain = Domain(
        domain=domain,
        subdomain=subdomain
    )
    db.session.add(new_domain)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'تم إضافة الدومين'})

@admin_bp.route('/domains/<int:domain_id>/toggle', methods=['POST'])
@login_required
def toggle_domain(domain_id):
    """تفعيل/إلغاء تفعيل دومين"""
    from models import Domain
    domain = Domain.query.get_or_404(domain_id)
    
    domain.is_active = not domain.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'تم {"تفعيل" if domain.is_active else "إلغاء تفعيل"} الدومين'
    })

@admin_bp.route('/stats')
@login_required
def get_stats():
    """إحصائيات إضافية للوحة التحكم"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(online=True).count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'verified_users': User.query.filter_by(verified=True).count(),
        'total_posts': Post.query.count(),
        'total_comments': Comment.query.count(),
        'total_likes': Like.query.count(),
        'pending_verification': VerificationRequest.query.filter_by(status='pending').count(),
    }
    
    # إحصائيات يومية
    today = datetime.utcnow().date()
    stats['today_posts'] = Post.query.filter(
        db.func.date(Post.created_at) == today
    ).count()
    stats['today_users'] = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()
    
    return jsonify(stats)
