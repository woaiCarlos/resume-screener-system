# resumes/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views, admin_views, auth_views

urlpatterns = [
    # 统一后台（唯一入口）
    path('', views.index, name='index'),

    # 登录页面
    path('login/', views.login_page, name='login_page'),

    # 认证 API
    path('api/auth/login/', auth_views.api_login, name='api_login'),
    path('api/auth/logout/', auth_views.api_logout, name='api_logout'),
    path('api/auth/me/', auth_views.api_me, name='api_me'),
    path('api/auth/csrf/', auth_views.api_csrf, name='api_csrf'),

    # 管理后台 API
    path('api/admin/positions/', admin_views.admin_positions, name='admin_positions'),
    path('api/admin/positions/<int:position_id>/', admin_views.admin_position_detail, name='admin_position_detail'),
    path('api/admin/resumes/', admin_views.admin_resumes, name='admin_resumes'),
    path('api/admin/resumes/<int:resume_id>/', admin_views.admin_resume_detail, name='admin_resume_detail'),
    path('api/admin/resumes/<int:resume_id>/download/', admin_views.admin_resume_download, name='admin_resume_download'),
    path('api/admin/batch-upload/', admin_views.admin_batch_upload, name='admin_batch_upload'),
    path('api/admin/stats/', admin_views.admin_stats, name='admin_stats'),
    path('api/admin/export/csv/', admin_views.admin_export_csv, name='admin_export_csv'),

    # 简历上传（兼容用户端）
    path('positions/<int:position_id>/upload/', views.upload_resume, name='upload_resume'),
    # 公开投递
    path('positions/<int:position_id>/apply/', views.apply_position, name='apply_position'),
    # 公开职位列表（用户端）
    path('positions/', views.position_list, name='position_list'),
]
