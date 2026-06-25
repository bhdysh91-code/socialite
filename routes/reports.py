from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Post, Report, Block
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

# ... باقي الكود

@reports_bp.route('/dashboard')
@login_required
def reports_dashboard():
    if not current_user.is_admin:
        flash('❌ غير مصرح', 'danger')
        return redirect(url_for('pages.index'))
    
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin_reports.html', user=current_user, reports=reports)
# ✅ الإبلاغ عن مستخدم
@reports_bp.route('/user/<int:user_id>', methods=['POST'])
@login_required
def report_user(user_id):
    reason = request.json.get('reason', '')
    report = Report(
        reporter_id=current_user.id,
        reported_id=user_id,
        type='user',
        reason=reason,
        status='pending'
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم الإبلاغ عن المستخدم'})

# ✅ الإبلاغ عن منشور
@reports_bp.route('/post/<int:post_id>', methods=['POST'])
@login_required
def report_post(post_id):
    reason = request.json.get('reason', '')
    report = Report(
        reporter_id=current_user.id,
        post_id=post_id,
        type='post',
        reason=reason,
        status='pending'
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم الإبلاغ عن المنشور'})

# ✅ حظر مستخدم
@reports_bp.route('/block/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    block = Block(blocker_id=current_user.id, blocked_id=user_id)
    db.session.add(block)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم حظر المستخدم'})

# ✅ إلغاء حظر مستخدم
@reports_bp.route('/unblock/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    block = Block.query.filter_by(blocker_id=current_user.id, blocked_id=user_id).first()
    if block:
        db.session.delete(block)
        db.session.commit()
    return jsonify({'success': True, 'message': 'تم إلغاء حظر المستخدم'})
# ✅ التحقق من عدد الإبلاغات على منشور
@reports_bp.route('/check/<int:post_id>')
@login_required
def check_reports(post_id):
    count = Report.query.filter_by(post_id=post_id, status='pending').count()
    
    if count >= 10:
        # ✅ حظر دائم
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'action': 'deleted', 'reason': 'تم حذف المنشور بسبب كثرة الإبلاغات'})
    
    elif count >= 5:
        # ✅ حظر مؤقت للمستخدم
        post = Post.query.get(post_id)
        if post:
            user = User.query.get(post.user_id)
            if user:
                user.is_banned = True
                db.session.commit()
                return jsonify({'action': 'banned', 'reason': 'تم حظر الحساب مؤقتاً'})
    
    elif count >= 3:
        # ✅ حذف المنشور
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'action': 'deleted', 'reason': 'تم حذف المنشور'})
    
    return jsonify({'action': 'pending', 'reason': 'جاري المراجعة', 'count': count})
