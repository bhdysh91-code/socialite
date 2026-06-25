from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import db, Notification, Message

api_bp = Blueprint('api', __name__)

@api_bp.route('/notifications/count')
@login_required
def notification_count():
    """عدد الإشعارات غير المقروءة"""
    count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
    return jsonify({'count': count})

@api_bp.route('/messages/unread/count')
@login_required
def unread_messages_count():
    """عدد الرسائل غير المقروءة"""
    count = Message.query.filter_by(receiver_id=current_user.id, read=False).count()
    return jsonify({'count': count})
