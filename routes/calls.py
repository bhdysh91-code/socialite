from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, Call, User, Notification
from datetime import datetime
import json

calls_bp = Blueprint('calls', __name__)

call_offers = {}
call_answers = {}
call_ice_candidates = {}
active_calls = {}

# ================================================================
# ✅ صفحات المكالمات
# ================================================================

@calls_bp.route('/audio/<int:user_id>')
@login_required
def call_audio(user_id):
    other_user = User.query.get_or_404(user_id)
    
    if hasattr(other_user, 'is_banned') and other_user.is_banned:
        return jsonify({'error': 'المستخدم محظور'}), 403
    
    call = Call(
        caller_id=current_user.id,
        receiver_id=user_id,
        type='audio',
        status='ringing'
    )
    db.session.add(call)
    db.session.commit()
    
    notif = Notification(
        user_id=user_id,
        type='call',
        from_user_id=current_user.id,
        message=f'{current_user.full_name} يتصل بك (صوتي)',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()
    
    active_calls[call.id] = {
        'caller_id': current_user.id,
        'receiver_id': user_id,
        'type': 'audio',
        'status': 'ringing'
    }
    
    return render_template('call.html', 
                         user=current_user, 
                         other_user=other_user, 
                         call_type='audio', 
                         call=call,
                         is_caller=True)

@calls_bp.route('/video/<int:user_id>')
@login_required
def call_video(user_id):
    other_user = User.query.get_or_404(user_id)
    
    if hasattr(other_user, 'is_banned') and other_user.is_banned:
        return jsonify({'error': 'المستخدم محظور'}), 403
    
    call = Call(
        caller_id=current_user.id,
        receiver_id=user_id,
        type='video',
        status='ringing'
    )
    db.session.add(call)
    db.session.commit()
    
    notif = Notification(
        user_id=user_id,
        type='call',
        from_user_id=current_user.id,
        message=f'{current_user.full_name} يتصل بك (فيديو)',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()
    
    active_calls[call.id] = {
        'caller_id': current_user.id,
        'receiver_id': user_id,
        'type': 'video',
        'status': 'ringing'
    }
    
    return render_template('call.html', 
                         user=current_user, 
                         other_user=other_user, 
                         call_type='video', 
                         call=call,
                         is_caller=True)

# ✅ مسار المكالمة الواردة
@calls_bp.route('/incoming/<int:call_id>')
@login_required
def incoming_call(call_id):
    """صفحة المكالمة الواردة للمستلم"""
    call = Call.query.get_or_404(call_id)
    caller = User.query.get(call.caller_id)
    
    if not caller:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    return render_template('call.html', 
                         user=current_user, 
                         other_user=caller, 
                         call_type=call.type, 
                         call=call,
                         is_caller=False)

# ================================================================
# ✅ API المكالمات
# ================================================================

@calls_bp.route('/api/start', methods=['POST'])
@login_required
def start_call():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    call_type = data.get('type', 'audio')
    
    if not receiver_id:
        return jsonify({'error': 'المستلم مطلوب'}), 400
    
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    call = Call(
        caller_id=current_user.id,
        receiver_id=receiver_id,
        type=call_type,
        status='ringing'
    )
    db.session.add(call)
    db.session.commit()
    
    notif = Notification(
        user_id=receiver_id,
        type='call',
        from_user_id=current_user.id,
        message=f'{current_user.full_name} يتصل بك ({call_type})',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()
    
    active_calls[call.id] = {
        'caller_id': current_user.id,
        'receiver_id': receiver_id,
        'type': call_type,
        'status': 'ringing'
    }
    
    return jsonify({
        'success': True,
        'call_id': call.id,
        'caller_name': current_user.full_name,
        'caller_avatar': current_user.avatar,
        'type': call_type,
        'receiver_id': receiver_id
    })

@calls_bp.route('/api/check/<int:user_id>')
@login_required
def check_call(user_id):
    call = Call.query.filter_by(
        receiver_id=user_id,
        status='ringing'
    ).first()
    
    if call:
        caller = User.query.get(call.caller_id)
        return jsonify({
            'has_call': True,
            'call_id': call.id,
            'caller_id': call.caller_id,
            'caller_name': caller.full_name if caller else '',
            'caller_avatar': caller.avatar if caller else '',
            'type': call.type
        })
    
    return jsonify({'has_call': False})

@calls_bp.route('/api/<int:call_id>/status')
@login_required
def call_status(call_id):
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'status': 'ended'})
    return jsonify({
        'status': call.status,
        'caller_id': call.caller_id,
        'receiver_id': call.receiver_id
    })

@calls_bp.route('/api/<int:call_id>/accept', methods=['POST'])
@login_required
def accept_call(call_id):
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'error': 'المكالمة غير موجودة'}), 404
    if call.receiver_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    call.status = 'active'
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم قبول المكالمة'})

@calls_bp.route('/api/<int:call_id>/reject', methods=['POST'])
@login_required
def reject_call(call_id):
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'error': 'المكالمة غير موجودة'}), 404
    if call.receiver_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    call.status = 'rejected'
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم رفض المكالمة'})

@calls_bp.route('/api/<int:call_id>/end', methods=['POST'])
@login_required
def end_call(call_id):
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'error': 'المكالمة غير موجودة'}), 404
    if call.caller_id != current_user.id and call.receiver_id != current_user.id:
        return jsonify({'error': 'غير مصرح'}), 403
    call.status = 'ended'
    call.ended_at = datetime.utcnow()
    if call.created_at:
        call.duration = int((call.ended_at - call.created_at).total_seconds())
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إنهاء المكالمة'})

@calls_bp.route('/api/<int:call_id>/offer', methods=['POST'])
@login_required
def send_offer(call_id):
    data = request.get_json()
    offer = data.get('offer')
    call_offers[call_id] = {'offer': offer, 'sender_id': current_user.id}
    return jsonify({'success': True})

@calls_bp.route('/api/<int:call_id>/answer', methods=['POST'])
@login_required
def send_answer(call_id):
    data = request.get_json()
    answer = data.get('answer')
    call_answers[call_id] = {'answer': answer, 'sender_id': current_user.id}
    return jsonify({'success': True})

@calls_bp.route('/api/<int:call_id>/ice', methods=['POST'])
@login_required
def send_ice(call_id):
    data = request.get_json()
    candidate = data.get('candidate')
    if call_id not in call_ice_candidates:
        call_ice_candidates[call_id] = []
    call_ice_candidates[call_id].append({'candidate': candidate, 'sender_id': current_user.id})
    return jsonify({'success': True})

@calls_bp.route('/api/<int:call_id>/get_offer')
@login_required
def get_offer(call_id):
    offer_data = call_offers.get(call_id)
    if offer_data and offer_data['sender_id'] != current_user.id:
        return jsonify({'offer': offer_data['offer']})
    return jsonify({'offer': None})

@calls_bp.route('/api/<int:call_id>/get_answer')
@login_required
def get_answer(call_id):
    answer_data = call_answers.get(call_id)
    if answer_data and answer_data['sender_id'] != current_user.id:
        return jsonify({'answer': answer_data['answer']})
    return jsonify({'answer': None})

@calls_bp.route('/api/<int:call_id>/get_ice')
@login_required
def get_ice(call_id):
    candidates = call_ice_candidates.get(call_id, [])
    result = []
    for c in candidates:
        if c['sender_id'] != current_user.id:
            result.append(c['candidate'])
    return jsonify({'candidates': result})
