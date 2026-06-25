import os
from datetime import datetime

LOG_DIR = 'logs'

def log_error(error_message, details=None):
    """تسجيل الأخطاء في ملف للمدير"""
    os.makedirs(LOG_DIR, exist_ok=True)
    filename = os.path.join(LOG_DIR, f'error_{datetime.now().strftime("%Y%m%d")}.log')
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now()}] ERROR: {error_message}")
        if details:
            f.write(f"\nDETAILS: {details}")
        f.write("\n" + "="*50)

def log_report(report_data):
    """تسجيل التقارير (إباحي، حظر، إلخ) في ملف للمدير"""
    os.makedirs(LOG_DIR, exist_ok=True)
    filename = os.path.join(LOG_DIR, f'reports_{datetime.now().strftime("%Y%m%d")}.log')
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now()}] REPORT: {report_data}")
        f.write("\n" + "="*50)
