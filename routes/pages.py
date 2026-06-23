from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Post, User

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', user=current_user, posts=posts)

@pages_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    users = []
    posts = []
    if query:
        users = User.query.filter(
            (User.username.contains(query)) | (User.full_name.contains(query)),
            User.id != current_user.id
        ).limit(20).all()
        posts = Post.query.filter(
            Post.text.contains(query)
        ).order_by(Post.created_at.desc()).limit(20).all()
    return render_template('search.html', user=current_user, query=query, users=users, posts=posts)

@pages_bp.route('/camera')
@login_required
def camera():
    return render_template('camera.html', user=current_user)

@pages_bp.route('/stories')
@login_required
def stories():
    return render_template('stories.html', user=current_user)

@pages_bp.route('/notifications')
@login_required
def notifications():
    from models import Notification
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    for n in notifs:
        n.read = True
    db.session.commit()
    return render_template('notifications.html', user=current_user, notifications=notifs)
