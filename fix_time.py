import sqlite3
from datetime import datetime

# إصلاح التوقيت في قاعدة البيانات
conn = sqlite3.connect('instance/facebook.db')
cursor = conn.cursor()

# تحديث توقيت المنشورات إلى الوقت الحالي
cursor.execute("UPDATE posts SET created_at = datetime('now')")
cursor.execute("UPDATE comments SET created_at = datetime('now')")

conn.commit()
conn.close()
print("✅ تم إصلاح التوقيت")
