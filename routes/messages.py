from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Message, User, Friendship
from datetime import datetime
import os
import base64

messages_bp = Blueprint('messages', __name__)

# تخزين المعاينة المباشرة
live_previews = {}

@messages_bp.route('/')
@login_required
def messages():
    friends = current_user.get_friends()
    return render_template('messages.html', user=current_user, friends=friends)

@messages_bp.route('/<int:user_id>')
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)
    
    is_friend = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
        ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id)),
        Friendship.status == 'accepted'
    ).first() is not None
    
    if current_user.id == user_id or is_friend:
        return render_template('chat.html', user=current_user, other_user=other_user)
    else:
        flash('❌ ليس لديك صلاحية للدردشة مع هذا المستخدم', 'danger')
        return redirect(url_for('messages.messages'))

@messages_bp.route('/api/get/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    result = []
    for m in messages:
        if m.deleted and m.sender_id != current_user.id:
            result.append({
                'id': m.id,
                'deleted': True,
                'sender_id': m.sender_id,
                'created_at': m.created_at.isoformat()
            })
            continue
        if m.deleted and m.sender_id == current_user.id:
            continue
        
        data = {
            'id': m.id,
            'sender_id': m.sender_id,
            'text': m.text or '',
            'created_at': m.created_at.isoformat(),
            'read': m.read,
            'deleted': False,
            'encrypted': m.encrypted if hasattr(m, 'encrypted') else False
        }
        if m.audio:
            data['audio'] = m.audio
        if m.image:
            data['image'] = m.image
        if m.video:
            data['video'] = m.video
        result.append(data)
    
    return jsonify(result)

@messages_bp.route('/api/send', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        text = data.get('text', '').strip()
        audio_data = data.get('audio')
        media_data = data.get('media')
        media_type = data.get('type', '')
        
        if not receiver_id:
            return jsonify({'error': 'المستلم مطلوب'}), 400
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        audio_path = None
        image_path = None
        video_path = None
        
        if audio_data:
            try:
                if ',' in audio_data:
                    audio_data = audio_data.split(',')[1]
                audio_bytes = base64.b64decode(audio_data)
                filename = f"audio_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.webm"
                filepath = os.path.join('static/uploads/audio', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(audio_bytes)
                audio_path = f'/static/uploads/audio/{filename}'
            except Exception as e:
                print(f"Error saving audio: {e}")
        
        if media_data:
            try:
                if ',' in media_data:
                    media_data = media_data.split(',')[1]
                media_bytes = base64.b64decode(media_data)
                ext = 'mp4' if media_type == 'video' else 'jpg'
                folder = 'videos' if media_type == 'video' else 'images'
                filename = f"{media_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.{ext}"
                filepath = os.path.join(f'static/uploads/{folder}', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(media_bytes)
                
                if media_type == 'video':
                    video_path = f'/static/uploads/videos/{filename}'
                else:
                    image_path = f'/static/uploads/images/{filename}'
            except Exception as e:
                print(f"Error saving media: {e}")
        
        encrypt_msg = receiver.encryption_enabled if receiver else False
        
        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            text=text or ('🎤 رسالة صوتية' if audio_path else '📸 صورة' if image_path else '🎬 فيديو' if video_path else ''),
            audio=audio_path,
            image=image_path,
            video=video_path,
            deleted=False,
            encrypted=encrypt_msg
        )
        db.session.add(msg)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم إرسال الرسالة'})
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/api/typing', methods=['POST'])
@login_required
def typing():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    text = data.get('text', '')
    is_typing = data.get('is_typing', False)
    if is_typing:
        live_previews[receiver_id] = {
            'user_name': current_user.full_name,
            'text': text
        }
    else:
        if receiver_id in live_previews:
            del live_previews[receiver_id]
    return jsonify({'success': True})

@messages_bp.route('/api/live-preview')
@login_required
def live_preview():
    preview = live_previews.get(current_user.id)
    if preview:
        return jsonify(preview)
    return jsonify({'text': ''})

# ================================================================
# ✅ حذف رسالة عادي
# ================================================================

@messages_bp.route('/api/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({'error': 'الرسالة غير موجودة'}), 404
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    msg.deleted = True
    db.session.commit()
    return jsonify({
        'success': True,
        'message_id': message_id,
        'receiver_id': msg.receiver_id
    })

# ================================================================
# ✅ الميزة 7: تشفير الرسالة
# ================================================================

@messages_bp.route('/api/encrypt/<int:message_id>', methods=['POST'])
@login_required
def encrypt_message(message_id):
    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({'error': 'الرسالة غير موجودة'}), 404
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    msg.encrypted = True
    db.session.commit()
    return jsonify({
        'success': True,
        'message_id': message_id,
        'encrypted_text': encrypt_text(msg.text)
    })

def encrypt_text(text):
    cipher_map = {
        'ا': '☯', 'ب': '◉', 'ت': '✦', 'ث': '✧', 'ج': '⬡',
        'ح': '❖', 'خ': '✦', 'د': '◈', 'ذ': '⟡', 'ر': '⌘',
        'ز': '⌂', 'س': '☰', 'ش': '☷', 'ص': '☲', 'ض': '☳',
        'ط': '☴', 'ظ': '☵', 'ع': '☶', 'غ': '☷', 'ف': '☸',
        'ق': '☹', 'ك': '☺', 'ل': '☻', 'م': '☼', 'ن': '☽',
        'ه': '☾', 'و': '☿', 'ي': '♁', ' ': '␣', '!': '❗',
        '؟': '❓', '.': '•', ',': '،', ';': '؛'
    }
    result = ''
    for char in text:
        result += cipher_map.get(char, char)
    return result

# ================================================================
# ✅ الميزة 13: حذف العاصفة
# ================================================================

@messages_bp.route('/api/storm-delete/<int:message_id>', methods=['POST'])
@login_required
def storm_delete(message_id):
    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({'error': 'الرسالة غير موجودة'}), 404
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    msg.deleted = True
    db.session.commit()
    return jsonify({
        'success': True,
        'message_id': message_id,
        'receiver_id': msg.receiver_id
    })
