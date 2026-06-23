from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from models import db, User, Message, Notification
from datetime import datetime
import base64
import os

socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        current_user.socket_id = request.sid
        current_user.online = True
        db.session.commit()
        emit('connected', {'status': 'online', 'user_id': current_user.id})

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        current_user.online = False
        current_user.last_seen = datetime.utcnow()
        current_user.socket_id = None
        db.session.commit()

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        join_room(room)
        emit('joined_room', {'room': room})

@socketio.on('send_message')
def handle_send_message(data):
    try:
        receiver_id = data.get('receiver_id')
        text = data.get('text', '')
        audio_data = data.get('audio')
        image_data = data.get('image')
        
        if not receiver_id:
            emit('error', {'message': 'المستلم مطلوب'})
            return
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            emit('error', {'message': 'المستخدم غير موجود'})
            return
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            text=text
        )
        
        if audio_data:
            audio_path = save_audio(audio_data, current_user.id, receiver_id)
            message.audio = audio_path
        
        if image_data:
            image_path = save_image_from_base64(image_data, current_user.id, receiver_id)
            message.image = image_path
        
        db.session.add(message)
        db.session.commit()
        
        notif = Notification(
            user_id=receiver_id,
            type='message',
            from_user_id=current_user.id,
            message=f'{current_user.full_name} أرسل لك رسالة'
        )
        db.session.add(notif)
        db.session.commit()
        
        room = f"user_{min(current_user.id, receiver_id)}_{max(current_user.id, receiver_id)}"
        emit('new_message', message.to_dict(), room=room)
        
        if receiver.socket_id:
            emit('new_notification', notif.to_dict(), room=receiver.socket_id)
        
    except Exception as e:
        print(f"Error sending message: {e}")
        emit('error', {'message': str(e)})

@socketio.on('typing')
def handle_typing(data):
    receiver_id = data.get('receiver_id')
    is_typing = data.get('is_typing', True)
    
    receiver = User.query.get(receiver_id)
    if receiver and receiver.socket_id:
        emit('typing', {
            'sender_id': current_user.id,
            'sender_name': current_user.full_name,
            'is_typing': is_typing
        }, room=receiver.socket_id)

@socketio.on('read_message')
def handle_read_message(data):
    message_id = data.get('message_id')
    if message_id:
        message = Message.query.get(message_id)
        if message and message.receiver_id == current_user.id:
            message.read = True
            message.read_at = datetime.utcnow()
            db.session.commit()

def save_audio(audio_base64, sender_id, receiver_id):
    try:
        audio_data = base64.b64decode(audio_base64)
        filename = f"audio_{sender_id}_{receiver_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.ogg"
        filepath = os.path.join('static/uploads/audio', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        return f'/static/uploads/audio/{filename}'
    except Exception as e:
        print(f"Error saving audio: {e}")
        return None

def save_image_from_base64(image_base64, sender_id, receiver_id):
    try:
        image_data = base64.b64decode(image_base64)
        filename = f"image_{sender_id}_{receiver_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join('static/uploads/images', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        return f'/static/uploads/images/{filename}'
    except Exception as e:
        print(f"Error saving image: {e}")
        return None
