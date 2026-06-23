from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Post, User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=current_user, profile_user=current_user, posts=posts)

@profile_bp.route('/<username>')
@login_required
def view_profile(username):
    profile_user = User.query.filter_by(username=username).first()
    if not profile_user:
        flash('❌ المستخدم غير موجود', 'danger')
        return redirect(url_for('pages.index'))
    posts = Post.query.filter_by(user_id=profile_user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=current_user, profile_user=profile_user, posts=posts)

@profile_bp.route('/toggle-encryption', methods=['POST'])
@login_required
def toggle_encryption():
    current_user.encryption_enabled = not current_user.encryption_enabled
    db.session.commit()
    status = "مفعل" if current_user.encryption_enabled else "معطل"
    return jsonify({
        'success': True,
        'encryption_enabled': current_user.encryption_enabled,
        'message': f'✅ تم {status} التشفير التلقائي'
    })
