from flask_socketio import emit, join_room, leave_room
from models import db, User, Call
from datetime import datetime

class WebRTCManager:
    active_calls = {}
    
    @staticmethod
    def init_socketio(socketio):
        @socketio.on('call_user')
        def handle_call(data):
            receiver_id = data.get('receiver_id')
            call_type = data.get('type', 'audio')
            
            receiver = User.query.get(receiver_id)
            if not receiver:
                emit('call_error', {'message': 'المستخدم غير موجود'})
                return
            
            if not receiver.online:
                emit('call_error', {'message': 'المستخدم غير متصل'})
                return
            
            call = Call(
                caller_id=current_user.id,
                receiver_id=receiver_id,
                type=call_type,
                status='ringing'
            )
            db.session.add(call)
            db.session.commit()
            
            room = f"call_{current_user.id}_{receiver_id}_{call.id}"
            join_room(room)
            
            WebRTCManager.active_calls[room] = {
                'caller': current_user.id,
                'receiver': receiver_id,
                'type': call_type,
                'call_id': call.id
            }
            
            if receiver.socket_id:
                emit('incoming_call', {
                    'call_id': call.id,
                    'caller_id': current_user.id,
                    'caller_name': current_user.full_name,
                    'caller_avatar': current_user.avatar,
                    'type': call_type,
                    'room': room
                }, room=receiver.socket_id)
            
            emit('call_initiated', {'room': room, 'call_id': call.id})

        @socketio.on('accept_call')
        def handle_accept_call(data):
            room = data.get('room')
            call_id = data.get('call_id')
            
            if room not in WebRTCManager.active_calls:
                emit('call_error', {'message': 'المكالمة غير موجودة'})
                return
            
            call = Call.query.get(call_id)
            if call:
                call.status = 'active'
                db.session.commit()
            
            join_room(room)
            emit('call_accepted', {'room': room}, room=room)

        @socketio.on('reject_call')
        def handle_reject_call(data):
            room = data.get('room')
            call_id = data.get('call_id')
            
            call = Call.query.get(call_id)
            if call:
                call.status = 'ended'
                call.ended_at = datetime.utcnow()
                db.session.commit()
            
            leave_room(room)
            if room in WebRTCManager.active_calls:
                del WebRTCManager.active_calls[room]
            
            emit('call_rejected', {}, room=room)

        @socketio.on('end_call')
        def handle_end_call(data):
            room = data.get('room')
            call_id = data.get('call_id')
            
            call = Call.query.get(call_id)
            if call:
                call.status = 'ended'
                call.ended_at = datetime.utcnow()
                if call.created_at:
                    call.duration = int((call.ended_at - call.created_at).total_seconds())
                db.session.commit()
            
            leave_room(room)
            if room in WebRTCManager.active_calls:
                del WebRTCManager.active_calls[room]
            
            emit('call_ended', {}, room=room)

        @socketio.on('webrtc_offer')
        def handle_webrtc_offer(data):
            room = data.get('room')
            offer = data.get('offer')
            emit('webrtc_offer', {'offer': offer}, room=room, include_self=False)

        @socketio.on('webrtc_answer')
        def handle_webrtc_answer(data):
            room = data.get('room')
            answer = data.get('answer')
            emit('webrtc_answer', {'answer': answer}, room=room, include_self=False)

        @socketio.on('webrtc_ice')
        def handle_webrtc_ice(data):
            room = data.get('room')
            candidate = data.get('candidate')
            emit('webrtc_ice', {'candidate': candidate}, room=room, include_self=False)
