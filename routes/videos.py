from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/')
@login_required
def videos_page():
    """صفحة عرض الفيديوهات"""
    return render_template('videos.html', user=current_user)

@videos_bp.route('/api/videos')
@login_required
def get_videos():
    """جلب فيديوهات تجريبية (مع video_id)"""
    videos = [
        {
            'title': 'فيديو تجريبي 1',
            'description': 'هذا فيديو تجريبي للاختبار',
            'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
            'video_id': 'dQw4w9WgXcQ'  # ✅ إضافة video_id
        },
        {
            'title': 'فيديو تجريبي 2',
            'description': 'فيديو آخر للاختبار',
            'thumbnail': 'https://img.youtube.com/vi/9bZkp7q19f0/hqdefault.jpg',
            'video_id': '9bZkp7q19f0'  # ✅ إضافة video_id
        }
    ]
    return jsonify({'success': True, 'videos': videos})
