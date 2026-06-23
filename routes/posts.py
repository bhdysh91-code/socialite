from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Post
import base64
import os
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/api/posts', methods=['GET'])
@login_required
def api_get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'text': p.text,
        'image': p.image,
        'user_name': p.author.full_name,
        'user_avatar': p.author.avatar,
        'created_at': p.created_at.isoformat()
    } for p in posts])

@posts_bp.route('/api/posts', methods=['POST'])
@login_required
def api_create_post():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        image_data = data.get('image')
        video_data = data.get('video')
        image_path = None
        video_path = None
        
        if image_data:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            filename = f"post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.jpg"
            filepath = os.path.join('static/uploads/posts', filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            image_path = f'/static/uploads/posts/{filename}'
        
        if video_data:
            if ',' in video_data:
                video_data = video_data.split(',')[1]
            video_bytes = base64.b64decode(video_data)
            filename = f"video_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.mp4"
            filepath = os.path.join('static/uploads/posts', filename)
            with open(filepath, 'wb') as f:
                f.write(video_bytes)
            video_path = f'/static/uploads/posts/{filename}'
        
        post = Post(
            user_id=current_user.id,
            text=text or '📸 محتوى جديد',
            image=image_path,
            created_at=datetime.utcnow()
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict(current_user.id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
