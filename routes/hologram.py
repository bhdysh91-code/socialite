from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Post

hologram_bp = Blueprint('hologram', __name__)

# ✅ المسار الصحيح (بدون /hologram مكرر)
@hologram_bp.route('/<int:post_id>')
@login_required
def hologram_view(post_id):
    """صفحة عرض الهولوغرام"""
    post = Post.query.get_or_404(post_id)
    return render_template('hologram.html', user=current_user, post=post)

@hologram_bp.route('/api/<int:post_id>')
@login_required
def get_hologram_data(post_id):
    """جلب بيانات المنشور بتنسيق 3D"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'المنشور غير موجود'}), 404
    
    hologram_data = {
        'id': post.id,
        'text': post.text,
        'user_name': post.author.full_name,
        'user_avatar': post.author.avatar,
        'layers': generate_3d_layers(post.text)
    }
    return jsonify(hologram_data)

def generate_3d_layers(text):
    """توليد طبقات ثلاثية الأبعاد من النص"""
    layers = []
    words = text.split()
    for i, word in enumerate(words):
        layers.append({
            'text': word,
            'depth': i * 5,
            'rotation': i * 10,
            'scale': 1 + (i * 0.05)
        })
    return layers
