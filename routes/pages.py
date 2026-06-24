from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Post, User, Article
from datetime import datetime
import time

pages_bp = Blueprint('pages', __name__)

# ... باقي الكود

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
@login_required
def fetch_news_api():
    """جلب آخر الأخبار من مصادر RSS"""
    try:
        import feedparser
        sources = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            'https://feeds.feedburner.com/alarabiya'
        ]
        count = 0
        for source in sources:
            feed = feedparser.parse(source)
            for entry in feed.entries[:5]:  # 5 مقالات من كل مصدر
                existing = Article.query.filter_by(link=entry.link).first()
                if not existing:
                    article = Article(
                        title=entry.title,
                        description=entry.description[:200] if hasattr(entry, 'description') else '',
                        link=entry.link,
                        source=feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else source,
                        image_url=entry.get('media_content', [{}])[0].get('url') if hasattr(entry, 'media_content') else None,
                        published_at=datetime.fromtimestamp(time.mktime(entry.published_parsed)) if hasattr(entry, 'published_parsed') else datetime.utcnow()
                    )
                    db.session.add(article)
                    count += 1
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
