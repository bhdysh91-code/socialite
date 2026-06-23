from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # ✅ تأكد من وجود هذا السطر

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200), default='https://i.pravatar.cc/150?img=1')
    online = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    encryption_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ ✅ ✅ أضف هاتين الدالتين هنا
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # ... باقي دوال User ...
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_friends(self):
        friendships = Friendship.query.filter(
            ((Friendship.user_id == self.id) | (Friendship.friend_id == self.id)),
            Friendship.status == 'accepted'
        ).all()
        friend_ids = []
        for f in friendships:
            if f.user_id == self.id:
                friend_ids.append(f.friend_id)
            else:
                friend_ids.append(f.user_id)
        return User.query.filter(User.id.in_(friend_ids)).all() if friend_ids else []

    def get_pending_requests(self):
        return Friendship.query.filter(
            Friendship.friend_id == self.id,
            Friendship.status == 'pending'
        ).all()

    def get_friend_suggestions(self, limit=10):
        friends = self.get_friends()
        friend_ids = [f.id for f in friends] + [self.id]
        suggestions = User.query.filter(
            ~User.id.in_(friend_ids),
            User.id != self.id,
            User.is_banned == False
        ).limit(limit).all()
        return suggestions

    def is_friend(self, user_id):
        friendship = Friendship.query.filter(
            ((Friendship.user_id == self.id) & (Friendship.friend_id == user_id)) |
            ((Friendship.user_id == user_id) & (Friendship.friend_id == self.id)),
            Friendship.status == 'accepted'
        ).first()
        return friendship is not None

    def has_pending_request(self, user_id):
        request = Friendship.query.filter(
            (Friendship.user_id == self.id) & (Friendship.friend_id == user_id) |
            (Friendship.user_id == user_id) & (Friendship.friend_id == self.id),
            Friendship.status == 'pending'
        ).first()
        return request is not None

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300))
    video = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    def get_likes_count(self):
        return Like.query.filter_by(post_id=self.id).count()

    def get_comments_count(self):
        return Comment.query.filter_by(post_id=self.id).count()

    def is_liked_by(self, user_id):
        return Like.query.filter_by(user_id=user_id, post_id=self.id).first() is not None

    def to_dict(self, current_user_id=None):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.author.full_name,
            'user_avatar': self.author.avatar,
            'verified': self.author.verified,
            'text': self.text,
            'image': self.image,
            'video': self.video,
            'likes_count': self.get_likes_count(),
            'comments_count': self.get_comments_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'liked': self.is_liked_by(current_user_id) if current_user_id else False
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='comments')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.author.full_name,
            'user_avatar': self.author.avatar,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_like'),)

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    message = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    audio = db.Column(db.String(300))
    image = db.Column(db.String(300))
    video = db.Column(db.String(300))
    deleted = db.Column(db.Boolean, default=False)
    encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
# ================================================================
# نموذج الإعلانات (Ads)
# ================================================================

class Ad(db.Model):
    __tablename__ = 'ads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300))  # صورة الإعلان
    video = db.Column(db.String(300))  # فيديو الإعلان
    link = db.Column(db.String(300))   # رابط الإعلان
    company = db.Column(db.String(100))  # اسم الشركة
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # تاريخ انتهاء الإعلان
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def is_expired(self):
        """التحقق من انتهاء الإعلان"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'image': self.image,
            'video': self.video,
            'link': self.link,
            'company': self.company,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'views': self.views,
            'clicks': self.clicks
        }

class Call(db.Model):
    __tablename__ = 'calls'
    id = db.Column(db.Integer, primary_key=True)
    caller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), default='audio')
    status = db.Column(db.String(20), default='ringing')
    duration = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    caller = db.relationship('User', foreign_keys=[caller_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            'id': self.id,
            'caller_id': self.caller_id,
            'caller_name': self.caller.full_name if self.caller else '',
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver.full_name if self.receiver else '',
            'type': self.type,
            'status': self.status,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
