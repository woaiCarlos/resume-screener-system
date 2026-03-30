# resumes/auth_decorators.py
# API 认证装饰器

from functools import wraps
from django.http import JsonResponse


def api_login_required(view_func):
    """API 登录认证装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': '请先登录', 'code': 'unauthorized'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
