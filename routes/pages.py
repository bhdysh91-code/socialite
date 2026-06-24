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
    """جلب آخر الأخبار من مصادر RSS"""

    try:
        import feedparser
        import time
        from datetime import datetime

        sources = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            'https://rss.cnn.com/rss/edition.rss',
            'https://www.reutersagency.com/feed/?best-topics=all',
            'https://feeds.skynews.com/feeds/rss/world.xml',

            'https://www.aljazeera.net/feed/rss',
            'https://www.alarabiya.net/feed/rss',
            'https://www.skynewsarabia.com/web/rss',
            'https://arabic.cnn.com/rss',

            'https://www.sabq.org/rss',
            'https://www.okaz.com.sa/rss',
            'https://www.alriyadh.com/rss.xml',
            'https://www.alwatan.com.sa/rss',
            'https://www.aleqt.com/rss',

            'https://www.albayan.ae/feed/rss',
            'https://www.emaratalyoum.com/feed/rss',

            'https://www.kooora.com/rss.aspx',
            'https://www.yallakora.com/rss',
            'https://www.espn.com/espn/rss/news',
            'https://sports.yahoo.com/rss/',
            'https://www.skysports.com/rss/12040',

            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml',
            'https://www.wired.com/feed/rss',
            'https://feeds.arstechnica.com/arstechnica/index',

            'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'https://www.marketwatch.com/rss/topstories',

            'https://www.sciencedaily.com/rss/all.xml',
        ]

        count = 0

        for source in sources:
            try:
                feed = feedparser.parse(source)

                for entry in feed.entries[:5]:

                    if not getattr(entry, 'link', None):
                        continue

                    existing = Article.query.filter_by(
                        link=entry.link
                    ).first()

                    if existing:
                        continue

                    description = ''

                    if hasattr(entry, 'description'):
                        description = entry.description[:300]

                    image_url = None

                    if hasattr(entry, 'media_content'):
                        try:
                            image_url = entry.media_content[0]['url']
                        except:
                            pass

                    published_at = datetime.utcnow()

                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime.fromtimestamp(
                            time.mktime(entry.published_parsed)
                        )

                    article = Article(
                        title=getattr(entry, 'title', 'بدون عنوان'),
                        description=description,
                        link=entry.link,
                        source=getattr(feed.feed, 'title', source),
                        image_url=image_url,
                        published_at=published_at
                    )

                    db.session.add(article)
                    count += 1

            except Exception as e:
                print(f"خطأ في المصدر {source}: {e}")

        db.session.commit()

        return jsonify({
            'success': True,
            'count': count
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
