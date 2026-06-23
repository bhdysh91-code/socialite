from flask import request, redirect, url_for, abort
from models import Domain
import re

class DomainManager:
    """إدارة الدومينات الفرعية"""
    
    @staticmethod
    def get_current_domain():
        """الحصول على الدومين الحالي"""
        host = request.host.split(':')[0]  # إزالة البورت
        return host
    
    @staticmethod
    def get_subdomain():
        """الحصول على الدومين الفرعي"""
        host = DomainManager.get_current_domain()
        parts = host.split('.')
        
        if len(parts) > 2:
            return parts[0]  # subdomain.facebook.local
        return None
    
    @staticmethod
    def is_valid_domain(domain):
        """التحقق من صحة الدومين"""
        pattern = r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
    
    @staticmethod
    def is_allowed_subdomain(subdomain):
        """التحقق من الدومين الفرعي المسموح"""
        from config import Config
        return subdomain in Config.ALLOWED_SUBDOMAINS
    
    @staticmethod
    def redirect_to_domain(target_domain):
        """إعادة توجيه إلى دومين معين"""
        return redirect(f"http://{target_domain}{request.path}")

class SubdomainMiddleware:
    """وسيط للتعامل مع الدومينات الفرعية"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # التحقق من الدومين
        host = environ.get('HTTP_HOST', '').split(':')[0]
        subdomain = host.split('.')[0] if len(host.split('.')) > 2 else None
        
        # إذا كان دومين فرعي غير مسموح
        if subdomain and subdomain not in ['www', 'admin', 'api', 'app', 'm']:
            # التحقق من قاعدة البيانات
            from models import Domain
            domain = Domain.query.filter_by(domain=host).first()
            if not domain or not domain.is_active:
                start_response('404 Not Found', [('Content-Type', 'text/html')])
                return [b'Domain not found']
        
        return self.app(environ, start_response)
