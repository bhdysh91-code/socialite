import feedparser
import requests
from datetime import datetime
from models import db, Article
import schedule
import time

# ✅ قائمة مصادر RSS
RSS_SOURCES = [
    'https://www.aljazeera.net/feed/rss',
    'https://www.alarabiya.net/feed/rss',
    'https://www.albayan.ae/feed/rss',
    'https://www.emaratalyoum.com/feed/rss',
    'https://www.skynewsarabia.com/feed/rss',
    'https://arabic.cnn.com/rss/latest',
    'https://www.youm7.com/RSS/News',
    'https://www.egypttoday.com/feed',
    'https://www.kooora.com/rss.aspx',
    'https://www.yallakora.com/rss',
]

def fetch_rss_news():
    """جلب الأخبار من جميع مصادر RSS (مع مهلة زمنية)"""
    count = 0
    for source in RSS_SOURCES:
        try:
            # ✅ استخدم requests للحصول على المحتوى مع مهلة زمنية
            response = requests.get(source, timeout=10)
            feed = feedparser.parse(response.content)
            
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
        except requests.exceptions.Timeout:
            print(f"⏰ مهلة زمنية لتجاوز المصدر: {source}")
        except Exception as e:
            print(f"❌ خطأ في {source}: {e}")
    
    db.session.commit()
    print(f"✅ تم جلب {count} خبر جديد")

# ✅ جدولة التحديث كل 5 دقائق
schedule.every(5).minutes.do(fetch_rss_news)

# ✅ تشغيل المهمة في الخلفية
def start_news_scheduler():
    print("🚀 بدء تشغيل مجدول الأخبار (كل 5 دقائق)")
    while True:
        schedule.run_pending()
        time.sleep(1)
