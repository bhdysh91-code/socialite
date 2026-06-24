from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.friends import friends_bp
from routes.messages import messages_bp
from routes.calls import calls_bp
from routes.profile import profile_bp
from routes.pages import pages_bp
from routes.hologram import hologram_bp
from routes.admin import admin_bp
from routes.ads import ads_bp
from routes.videos import videos_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(friends_bp, url_prefix='/friends')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(calls_bp, url_prefix='/calls')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(pages_bp, url_prefix='')
    app.register_blueprint(hologram_bp, url_prefix='/hologram')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ads_bp, url_prefix='/ads')
    app.register_blueprint(videos_bp, url_prefix='/videos')
