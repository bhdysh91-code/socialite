from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Post, User, Article
from datetime import datetime
import time

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', user=current_user, posts=posts)

@pages_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    users = []
    posts = []
    if query:
        users = User.query.filter(
            (User.username.contains(query)) | (User.full_name.contains(query)),
            User.id != current_user.id
        ).limit(20).all()
        posts = Post.query.filter(
            Post.text.contains(query)
        ).order_by(Post.created_at.desc()).limit(20).all()
    return render_template('search.html', user=current_user, query=query, users=users, posts=posts)

@pages_bp.route('/camera')
@login_required
def camera():
    return render_template('camera.html', user=current_user)

@pages_bp.route('/stories')
@login_required
def stories():
    return render_template('stories.html', user=current_user)

# ================================================================
# ✅ API لجلب الأخبار يدوياً
# ================================================================
@pages_bp.route('/api/fetch-news', methods=['POST'])
def fetch_news_api():
    """جلب آخر الأخبار من مصادر RSS (عربية وعالمية ورياضية)"""
    try:
        import feedparser

        sources = [
            # عالمية
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            # عربية عامة
            'https://www.aljazeera.net/feed/rss',
            'https://www.alarabiya.net/feed/rss',
            # رياضية عربية
            'https://www.kooora.com/rss.aspx',
            'https://www.yallakora.com/rss',
            # إماراتية
            'https://www.albayan.ae/feed/rss',
            'https://www.emaratalyoum.com/feed/rss',
            # رياضية عالمية
            'https://www.espn.com/espn/rss/news',
            'https://sports.yahoo.com/rss/',
        ]
        
        count = 0
        for source in sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:5]:
                    existing = Article.query.filter_by(link=entry.link).first()
                    if not existing:
                        article = Article(
                            title=entry.title,
                            description=entry.description[:300] if hasattr(entry, 'description') else '',
                            link=entry.link,
                            source=feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else source,
                            image_url=entry.get('media_content', [{}])[0].get('url') if hasattr(entry, 'media_content') else None,
                            published_at=datetime.fromtimestamp(time.mktime(entry.published_parsed)) if hasattr(entry, 'published_parsed') else datetime.utcnow()
                        )
                        db.session.add(article)
                        count += 1
            except Exception as e:
                print(f"خطأ في المصدر {source}: {e}")
                continue
                
        db.session.commit()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pages_bp.route('/notifications')
@login_required
def notifications():
    from models import Notification
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    for n in notifs:
        n.read = True
    db.session.commit()
    return render_template('notifications.html', user=current_user, notifications=notifs)

# ================================================================
# ✅ صفحة عرض الأخبار
# ================================================================

@pages_bp.route('/news')
@login_required
def news_feed():
    """عرض آخر الأخبار المستوردة"""
    articles = Article.query.order_by(Article.published_at.desc()).limit(30).all()
    return render_template('news_feed.html', user=current_user, articles=articles)
# ================================================================
# ✅ بحث متقدم (يشمل فيديوهات وأخبار)
# ================================================================

@pages_bp.route('/search-advanced')
@login_required
def search_advanced():
    query = request.args.get('q', '').strip()
    users = []
    articles = []
    videos = []
    
    if query:
        # ✅ بحث في المستخدمين
        users = User.query.filter(
            (User.username.contains(query)) | (User.full_name.contains(query)),
            User.id != current_user.id
        ).limit(10).all()
        
        # ✅ بحث في الأخبار
        articles = Article.query.filter(
            (Article.title.contains(query)) | (Article.description.contains(query))
        ).order_by(Article.published_at.desc()).limit(10).all()
        
        # ✅ بحث في الفيديوهات (محاكاة)
        # في الواقع، سنستخدم API يوتيوب للبحث الحقيقي
        videos = [
            {'title': f'فيديو عن {query} - 1', 'description': 'هذا فيديو تجريبي', 'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg', 'video_id': 'dQw4w9WgXcQ'},
            {'title': f'فيديو عن {query} - 2', 'description': 'فيديو آخر', 'thumbnail': 'https://img.youtube.com/vi/9bZkp7q19f0/hqdefault.jpg', 'video_id': '9bZkp7q19f0'}
        ]
    
    return render_template('search_advanced.html', user=current_user, query=query, users=users, articles=articles, videos=videos)
