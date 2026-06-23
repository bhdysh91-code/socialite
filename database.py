from models import db, User, Post, Comment, Like, Friendship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    @staticmethod
    def init_db(app):
        """تهيئة قاعدة البيانات"""
        with app.app_context():
            db.create_all()
            
            # إنشاء مستخدمين افتراضيين إذا كانت قاعدة البيانات فارغة
            if User.query.count() == 0:
                Database.create_sample_users()
    
    @staticmethod
    def create_sample_users():
        """إنشاء مستخدمين عينة"""
        users_data = [
            {'username': 'ahmed', 'email': 'ahmed@example.com', 'password': '123456', 'full_name': 'أحمد محمد'},
            {'username': 'sara', 'email': 'sara@example.com', 'password': '123456', 'full_name': 'سارة علي'},
            {'username': 'mohammed', 'email': 'mohammed@example.com', 'password': '123456', 'full_name': 'محمد خالد'},
            {'username': 'fatima', 'email': 'fatima@example.com', 'password': '123456', 'full_name': 'فاطمة حسن'},
            {'username': 'khalid', 'email': 'khalid@example.com', 'password': '123456', 'full_name': 'خالد عبدالله'},
            {'username': 'layla', 'email': 'layla@example.com', 'password': '123456', 'full_name': 'ليلى ناصر'},
            {'username': 'nora', 'email': 'nora@example.com', 'password': '123456', 'full_name': 'نورة سعيد'},
            {'username': 'raneem', 'email': 'raneem@example.com', 'password': '123456', 'full_name': 'Raneem Zubaidi'},
        ]
        
        for data in users_data:
            user = User(
                username=data['username'],
                email=data['email'],
                password=generate_password_hash(data['password']),
                full_name=data['full_name'],
                avatar=f"https://i.pravatar.cc/150?img={len(users_data) + 1}",
                online=True,
                verified=data['username'] in ['raneem', 'ahmed']
            )
            db.session.add(user)
        
        db.session.commit()
        
        # إنشاء منشورات عينة
        users = User.query.all()
        sample_posts = [
            "مرحباً بالجميع في فيسبوك الحقيقي! 🚀",
            "هذا أول منشور لي هنا 🌟",
            "أتمنى لكم يوماً سعيداً ☀️",
            "فيسبوك أصبح أفضل بكثير الآن! 💪",
            "شاركونا آرائكم ❤️",
            "الحياة جميلة مع الأصدقاء 👥",
            "نتعلم ونتطور معاً 📚",
            "شكراً لكم على هذا المجتمع الرائع 🌸"
        ]
        
        for i, post_text in enumerate(sample_posts):
            user = users[i % len(users)]
            post = Post(
                user_id=user.id,
                text=post_text,
                image=f"https://images.unsplash.com/photo-{1500000000000 + i}?w=600&h=400&fit=crop" if i % 3 == 0 else None,
                created_at=datetime.now()
            )
            db.session.add(post)
        
        db.session.commit()
    
    @staticmethod
    def get_user_by_username(username):
        """الحصول على مستخدم بواسطة اسم المستخدم"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email):
        """الحصول على مستخدم بواسطة البريد الإلكتروني"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create_user(username, email, password, full_name):
        """إنشاء مستخدم جديد"""
        if User.query.filter_by(username=username).first():
            return None, "اسم المستخدم موجود بالفعل"
        if User.query.filter_by(email=email).first():
            return None, "البريد الإلكتروني موجود بالفعل"
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            full_name=full_name,
            avatar=f"https://i.pravatar.cc/150?img={User.query.count() + 10}"
        )
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    def authenticate_user(username, password):
        """مصادقة المستخدم"""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            user.online = True
            user.last_seen = datetime.now()
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def create_post(user_id, text, image=None, video=None):
        """إنشاء منشور جديد"""
        post = Post(
            user_id=user_id,
            text=text,
            image=image,
            video=video
        )
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def get_posts(page=1, per_page=10):
        """الحصول على المنشورات مع ترقيم الصفحات"""
        posts = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return posts
    
    @staticmethod
    def get_post_by_id(post_id):
        """الحصول على منشور بواسطة المعرف"""
        return Post.query.get(post_id)
    
    @staticmethod
    def toggle_like(user_id, post_id):
        """تبديل الإعجاب (إعجاب/إلغاء إعجاب)"""
        like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return False  # تم إلغاء الإعجاب
        else:
            like = Like(user_id=user_id, post_id=post_id)
            db.session.add(like)
            db.session.commit()
            return True  # تم الإعجاب
    
    @staticmethod
    def add_comment(user_id, post_id, text):
        """إضافة تعليق جديد"""
        comment = Comment(
            user_id=user_id,
            post_id=post_id,
            text=text
        )
        db.session.add(comment)
        db.session.commit()
        return comment
    
    @staticmethod
    def delete_comment(comment_id, user_id):
        """حذف تعليق (فقط إذا كان المستخدم هو صاحب التعليق)"""
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:
            db.session.delete(comment)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_online_friends(user_id):
        """الحصول على أصدقاء المستخدم المتصلين"""
        friendships = Friendship.query.filter(
            (Friendship.user_id == user_id) | (Friendship.friend_id == user_id),
            Friendship.status == 'accepted'
        ).all()
        
        friend_ids = []
        for f in friendships:
            if f.user_id == user_id:
                friend_ids.append(f.friend_id)
            else:
                friend_ids.append(f.user_id)
        
        return User.query.filter(
            User.id.in_(friend_ids),
            User.online == True
        ).all()
    
    @staticmethod
    def suggest_friends(user_id):
        """اقتراح أصدقاء جدد"""
        # الحصول على أصدقاء المستخدم
        friendships = Friendship.query.filter(
            (Friendship.user_id == user_id) | (Friendship.friend_id == user_id),
            Friendship.status == 'accepted'
        ).all()
        
        friend_ids = [user_id]
        for f in friendships:
            if f.user_id == user_id:
                friend_ids.append(f.friend_id)
            else:
                friend_ids.append(f.user_id)
        
        # اقتراح مستخدمين ليسوا أصدقاء
        suggestions = User.query.filter(
            ~User.id.in_(friend_ids),
            User.id != user_id
        ).limit(10).all()
        
        return suggestions
    
    @staticmethod
    def add_friend(user_id, friend_id):
        """إضافة صديق"""
        existing = Friendship.query.filter(
            ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
        ).first()
        
        if existing:
            return False, "طلب الصداقة موجود بالفعل"
        
        friendship = Friendship(
            user_id=user_id,
            friend_id=friend_id,
            status='accepted'
        )
        db.session.add(friendship)
        db.session.commit()
        return True, "تم إضافة الصديق بنجاح"
