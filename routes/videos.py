from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
import requests

videos_bp = Blueprint('videos', __name__)

# ✅ قائمة قنوات عربية (YouTube)
CHANNELS = [
    'UCe0TLA0EsQbE-MjuHXevj2A',  # العربية
    'UC6ZcW6iBs5Xxgf9AqB3rM2A',  # الجزيرة
    'UCq3RkXbRc4y0JmG9d0xXvEw',  # MBC
]

@videos_bp.route('/api/videos')
@login_required
def get_videos():
    """جلب فيديوهات من قنوات YouTube"""
    try:
        # API Key من Google (سجل للحصول على مفتاح)
        API_KEY = 'YOUR_YOUTUBE_API_KEY'
        videos = []
        
        for channel_id in CHANNELS:
            url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet&order=date&maxResults=5'
            response = requests.get(url)
            data = response.json()
            
            for item in data.get('items', []):
                videos.append({
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'video_id': item['id']['videoId'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })
        
        return jsonify({'success': True, 'videos': videos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@videos_bp.route('/videos')
@login_required
def videos_page():
    """صفحة عرض الفيديوهات"""
    return render_template('videos.html', user=current_user)
