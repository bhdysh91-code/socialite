import requests
import base64
import os
from datetime import datetime

# ✅ استخدام API مجاني للكشف عن المحتوى الإباحي
# (بدون مفتاح، استخدام نموذج بسيط)
NSFW_KEYWORDS = [
    'سكس', 'جنس', 'عاري', 'عارية', 'بورن', 'porn', 'sex', 'nude', 'fuck', 'xxx',
    'إباحي', 'إباحية', 'ممنوع', 'عري', 'سافل', 'خليع', 'فاضح'
]

def check_nsfw_text(text):
    """التحقق من نص إذا كان يحتوي على كلمات إباحية"""
    if not text:
        return False
    text_lower = text.lower()
    for word in NSFW_KEYWORDS:
        if word in text_lower:
            return True
    return False

def check_nsfw_image(image_url):
    """التحقق من صورة إذا كانت إباحية (باستخدام API خارجي)"""
    try:
        # ✅ استخدام API مجاني (بدون مفتاح)
        api_url = 'https://api.sightengine.com/1.0/check.json'
        params = {
            'url': image_url,
            'models': 'nudity',
            'api_user': 'your_api_user',  # سجل في sightengine.com
            'api_secret': 'your_api_secret'
        }
        response = requests.get(api_url, params=params, timeout=5)
        data = response.json()
        
        # ✅ نسبة الإباحية
        nsfw_score = data.get('nudity', {}).get('raw', 0)
        return nsfw_score > 0.5  # إذا كانت النسبة أكبر من 50%
    except:
        return False

def log_nsfw_content(content_type, content_id, reason):
    """تسجيل المحتوى المحظور في ملف للمدير"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    filename = os.path.join(log_dir, f'nsfw_log_{datetime.now().strftime("%Y%m%d")}.log')
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now()}] 🚫 محتوى محظور")
        f.write(f"\nالنوع: {content_type}")
        f.write(f"\nالمعرف: {content_id}")
        f.write(f"\nالسبب: {reason}")
        f.write("\n" + "="*50)
