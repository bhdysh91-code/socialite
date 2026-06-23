from flask import Blueprint, request, jsonify, render_template, url_for
from flask_login import login_required, current_user
from models import db, Friendship, Notification
from datetime import datetime

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/')
@login_required
def friends():
    friends_list = current_user.get_friends()
    pending_requests = current_user.get_pending_requests()
    suggestions = current_user.get_friend_suggestions(10)
    return render_template('friends.html',
                         user=current_user,
                         friends=friends_list,
                         pending=pending_requests,
                         suggestions=suggestions)

@friends_bp.route('/request/<int:user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'لا يمكنك إضافة نفسك'}), 400
    existing = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
        ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
    ).first()
    if existing:
        return jsonify({'error': 'طلب موجود بالفعل'}), 400
    friendship = Friendship(user_id=current_user.id, friend_id=user_id, status='pending')
    db.session.add(friendship)
    db.session.commit()
    notif = Notification(
        user_id=user_id,
        type='friend_request',
        from_user_id=current_user.id,
        message=f'{current_user.full_name} أرسل لك طلب صداقة',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إرسال طلب الصداقة'})

@friends_bp.route('/accept/<int:user_id>', methods=['POST'])
@login_required
def accept_request(user_id):
    friendship = Friendship.query.filter_by(
        user_id=user_id,
        friend_id=current_user.id,
        status='pending'
    ).first()
    if not friendship:
        return jsonify({'error': 'الطلب غير موجود'}), 404
    friendship.status = 'accepted'
    db.session.commit()
    notif = Notification(
        user_id=user_id,
        type='friend_accepted',
        from_user_id=current_user.id,
        message=f'{current_user.full_name} قبل طلب صداقتك',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()
    
    # ✅ إرجاع رابط الدردشة
    chat_url = url_for('messages.chat', user_id=user_id)
    return jsonify({
        'success': True, 
        'message': 'تم قبول الطلب',
        'chat_url': chat_url
    })

@friends_bp.route('/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_request(user_id):
    friendship = Friendship.query.filter_by(
        user_id=user_id,
        friend_id=current_user.id,
        status='pending'
    ).first()
    if not friendship:
        return jsonify({'error': 'الطلب غير موجود'}), 404
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم رفض الطلب'})

@friends_bp.route('/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
        ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id)),
        Friendship.status == 'accepted'
    ).first()
    if not friendship:
        return jsonify({'error': 'ليس صديقاً'}), 400
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إزالة الصديق'})
