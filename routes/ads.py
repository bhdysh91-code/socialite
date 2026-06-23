from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Ad, User
from datetime import datetime, timedelta
import os
import base64

ads_bp = Blueprint('ads', __name__)

# ================================================================
# دوال التحقق من صلاحيات المدير
# ================================================================

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        return False
    return True

# ================================================================
# صفحة إدارة الإعلانات (للمدير فقط)
# ================================================================

@ads_bp.route('/')
@login_required
def ads_dashboard():
    if not admin_required():
        flash('❌ غير مصرح', 'danger')
        return redirect(url_for('pages.index'))
    
    ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return render_template('admin_ads.html', user=current_user, ads=ads)

# ================================================================
# إنشاء إعلان جديد
# ================================================================

@ads_bp.route('/create', methods=['POST'])
@login_required
def create_ad():
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    data = request.get_json()
    title = data.get('title', '').strip()
    text = data.get('text', '').strip()
    company = data.get('company', '').strip()
    link = data.get('link', '').strip()
    image_data = data.get('image')
    video_data = data.get('video')
    duration_hours = data.get('duration_hours', 24)  # المدة بالساعات
    
    if not title or not text:
        return jsonify({'error': 'العنوان والنص مطلوبان'}), 400
    
    image_path = None
    video_path = None
    
    # حفظ الصورة
    if image_data:
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            filename = f"ad_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.jpg"
            filepath = os.path.join('static/uploads/ads', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            image_path = f'/static/uploads/ads/{filename}'
        except Exception as e:
            print(f"Error saving ad image: {e}")
    
    # حفظ الفيديو
    if video_data:
        try:
            if ',' in video_data:
                video_data = video_data.split(',')[1]
            video_bytes = base64.b64decode(video_data)
            filename = f"ad_video_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.id}.mp4"
            filepath = os.path.join('static/uploads/ads', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(video_bytes)
            video_path = f'/static/uploads/ads/{filename}'
        except Exception as e:
            print(f"Error saving ad video: {e}")
    
    # إنشاء الإعلان
    ad = Ad(
        title=title,
        text=text,
        image=image_path,
        video=video_path,
        link=link,
        company=company,
        created_by=current_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=duration_hours),
        is_active=True
    )
    db.session.add(ad)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '✅ تم إنشاء الإعلان بنجاح',
        'ad': ad.to_dict()
    })

# ================================================================
# حذف إعلان
# ================================================================

@ads_bp.route('/delete/<int:ad_id>', methods=['POST'])
@login_required
def delete_ad(ad_id):
    if not admin_required():
        return jsonify({'error': 'غير مصرح'}), 403
    
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '✅ تم حذف الإعلان'})

# ================================================================
# API: جلب الإعلانات النشطة (للعرض في الصفحة الرئيسية)
# ================================================================

@ads_bp.route('/api/active')
@login_required
def get_active_ads():
    now = datetime.utcnow()
    ads = Ad.query.filter(
        Ad.is_active == True,
        Ad.expires_at > now
    ).all()
    
    # تحديث عدد المشاهدات
    for ad in ads:
        ad.views += 1
    db.session.commit()
    
    return jsonify([ad.to_dict() for ad in ads])

# ================================================================
# تسجيل نقرة على الإعلان
# ================================================================

@ads_bp.route('/api/click/<int:ad_id>', methods=['POST'])
@login_required
def click_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    ad.clicks += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'link': ad.link or '#'
    })
