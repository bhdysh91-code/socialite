import sqlite3
import os

db_path = 'instance/facebook.db'

if os.path.exists(db_path):
    print("📂 جاري إصلاح قاعدة البيانات...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # الحصول على أسماء الأعمدة الموجودة
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # إضافة الأعمدة المفقودة
    new_columns = {
        'bio': 'TEXT DEFAULT ""',
        'cover_photo': 'TEXT DEFAULT ""',
        'birthday': 'DATE',
        'country': 'TEXT DEFAULT ""',
        'city': 'TEXT DEFAULT ""',
        'gender': 'TEXT DEFAULT ""',
        'last_seen': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }
    
    for col, col_type in new_columns.items():
        if col not in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
                print(f"✅ تم إضافة العمود: {col}")
            except Exception as e:
                print(f"⚠️ خطأ في إضافة {col}: {e}")
    
    # إضافة أعمدة لمنشورات جديدة
    cursor.execute("PRAGMA table_info(posts)")
    post_columns = [col[1] for col in cursor.fetchall()]
    
    post_new_columns = {
        'image': 'TEXT DEFAULT ""',
        'video': 'TEXT DEFAULT ""',
        'privacy': 'TEXT DEFAULT "public"',
        'shares': 'INTEGER DEFAULT 0'
    }
    
    for col, col_type in post_new_columns.items():
        if col not in post_columns:
            try:
                cursor.execute(f"ALTER TABLE posts ADD COLUMN {col} {col_type}")
                print(f"✅ تم إضافة العمود: {col} (posts)")
            except Exception as e:
                print(f"⚠️ خطأ في إضافة {col}: {e}")
    
    conn.commit()
    conn.close()
    print("✅ تم إصلاح قاعدة البيانات بنجاح!")
else:
    print("⚠️ قاعدة البيانات غير موجودة، سيتم إنشاؤها تلقائياً")
