from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Post, Message, Notification, Friendship, Call
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ✅ التحقق من صلاحيات المالك
def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        return False
    return True

@admin_bp.route('/')
@login_required
def dashboard():
    if not admin_required():
        flash('❌ غير مصرح لك بدخول لوحة التحكم', 'danger')
        return redirect(url_for('pages.index'))
    
    # إحصائيات
    stats = {
        'users': User.query.count(),
        'posts': Post.query.count(),
        'messages': Message.query.count(),
        'notifications': Notification.query.count(),
        'friendships': Friendship.query.count(),
        'calls': Call.query.count(),
        'banned': User.query.filter_by(is_banned=True).count(),
        'verified': User.query.filter_by(verified=True).count()
    }
    
    # آخر المستخدمين
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    
    return render_template('admin.html', 
                         user=current_user, 
                         stats=stats,
                         recent_users=recent_users,
                         recent_posts=recent_posts)

@admin_bp.route('/users')
@login_required
def users():
    if not admin_required():
        return redirect(url_for('pages.index'))
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', user=current_user, users=all_users)

@admin_bp.route('/users/<int:user_id>/toggle-ban', methods=['POST'])
@login_required
def toggle_ban(user_id):
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    if target_user.is_admin:
        return jsonify({'error': 'لا يمكن حظر مدير'}), 400
    
    target_user.is_banned = not target_user.is_banned
    db.session.commit()
    
    status = "محظور" if target_user.is_banned else "غير محظور"
    return jsonify({
        'success': True,
        'message': f'✅ تم {status} المستخدم {target_user.full_name}',
        'is_banned': target_user.is_banned
    })

@admin_bp.route('/users/<int:user_id>/toggle-verify', methods=['POST'])
@login_required
def toggle_verify(user_id):
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    target_user = User.query.get_or_404(user_id)
    
    target_user.verified = not target_user.verified
    db.session.commit()
    
    status = "موثق" if target_user.verified else "غير موثق"
    return jsonify({
        'success': True,
        'message': f'✅ تم {status} المستخدم {target_user.full_name}',
        'verified': target_user.verified
    })

@admin_bp.route('/posts')
@login_required
def posts():
    if not admin_required():
        return redirect(url_for('pages.index'))
    
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin_posts.html', user=current_user, posts=all_posts)

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '✅ تم حذف المنشور'})

@admin_bp.route('/messages')
@login_required
def messages():
    if not admin_required():
        return redirect(url_for('pages.index'))
    
    all_messages = Message.query.order_by(Message.created_at.desc()).limit(100).all()
    return render_template('admin_messages.html', user=current_user, messages=all_messages)

@admin_bp.route('/stats')
@login_required
def stats():
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    stats = {
        'total_users': User.query.count(),
        'online_users': User.query.filter_by(online=True).count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'verified_users': User.query.filter_by(verified=True).count(),
        'total_posts': Post.query.count(),
        'total_messages': Message.query.count(),
        'total_friendships': Friendship.query.count(),
        'total_calls': Call.query.count()
    }
    
    return jsonify(stats)
