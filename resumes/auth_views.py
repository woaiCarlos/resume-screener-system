# resumes/auth_views.py
# 用户认证 API

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """用户登录"""
    try:
        body = json.loads(request.body)
        username = body.get('username', '')
        password = body.get('password', '')

        if not username or not password:
            return JsonResponse({'error': '用户名和密码不能为空'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            })
        else:
            return JsonResponse({'error': '用户名或密码错误'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def api_logout(request):
    """用户登出"""
    logout(request)
    return JsonResponse({'success': True})


@require_http_methods(["GET"])
def api_me(request):
    """获取当前用户信息"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        })
    return JsonResponse({'authenticated': False, 'user': None})


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_csrf(request):
    """获取 CSRF Token"""
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE', '')})
