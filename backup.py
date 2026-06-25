import os
import shutil
from datetime import datetime
import schedule
import time

BACKUP_DIR = 'backups'

def create_backup():
    """إنشاء نسخة احتياطية كاملة للمشروع"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'socialite_backup_{timestamp}')
    
    # ✅ نسخ قاعدة البيانات والمجلدات المهمة
    os.makedirs(backup_path, exist_ok=True)
    
    # ✅ نسخ قاعدة البيانات
    shutil.copy('instance/socialite.db', os.path.join(backup_path, 'socialite.db'))
    
    # ✅ نسخ المجلدات
    for folder in ['static/uploads', 'templates', 'routes']:
        src = folder
        dst = os.path.join(backup_path, folder)
        if os.path.exists(src):
            shutil.copytree(src, dst)
    
    # ✅ إنشاء ملف log
    with open(os.path.join(backup_path, 'backup_log.txt'), 'w') as f:
        f.write(f"تم إنشاء النسخة الاحتياطية في: {datetime.now()}")
    
    print(f"✅ تم إنشاء النسخة الاحتياطية: {backup_path}")

# ✅ جدولة النسخ الاحتياطي يومياً
schedule.every().day.at("03:00").do(create_backup)

def start_backup_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)
