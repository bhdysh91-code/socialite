from flask import Blueprint, request, jsonify
from utils.nsfw_checker import check_nsfw_text, check_nsfw_image, log_nsfw_content
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
        
        # ✅ ✅ ✅ فلترة المحتوى الإباحي
        if text and check_nsfw_text(text):
            log_nsfw_content('نص', current_user.id, f'نص إباحي: {text[:50]}')
            return jsonify({'error': '❌ المحتوى غير مسموح به (يحتوي على كلمات ممنوعة)'}), 403
        
        # ... باقي الكود (حفظ الصورة والفيديو)
        
        # ✅ فلترة الصورة بعد الحفظ (اختياري)
        if image_path and check_nsfw_image(image_path):
            # حذف الصورة
            if os.path.exists(image_path):
                os.remove(image_path)
            log_nsfw_content('صورة', current_user.id, 'صورة إباحية')
            return jsonify({'error': '❌ الصورة غير مسموح بها'}), 403
        
        # ... حفظ المنشور
        post = Post(...)
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict(current_user.id))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
