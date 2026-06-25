from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from config import YOUTUBE_API_KEY
import requests

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/')
@login_required
def videos_page():
    """صفحة عرض الشورت فيديوهات"""
    return render_template('videos.html', user=current_user)

@videos_bp.route('/api/shorts')
@login_required
def get_shorts():
    """جلب شورت فيديوهات من يوتيوب"""
    try:
        # ✅ البحث عن فيديوهات قصيرة (Shorts)
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q=shorts&type=video&videoDuration=short&maxResults=50&key={YOUTUBE_API_KEY}'
        response = requests.get(url)
        data = response.json()
        
        shorts = []
        for item in data.get('items', []):
            shorts.append({
                'title': item['snippet']['title'],
                'video_id': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channel': item['snippet']['channelTitle']
            })
        
        return jsonify({'success': True, 'shorts': shorts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
