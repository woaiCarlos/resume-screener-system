# resumes/views.py
# 简历筛选系统 - 统一后台视图

import json
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import JobPosition, Resume
from .parser import ResumeParser, ResumeScreener


def index(request):
    """统一后台首页"""
    return render(request, 'admin.html')


def login_page(request):
    """登录页面"""
    return render(request, 'login.html')


def position_list(request):
    """公开职位列表页面"""
    positions = JobPosition.objects.all().order_by('-created_at')
    positions_data = []
    for p in positions:
        positions_data.append({
            'id': p.id,
            'title': p.title,
            'description': p.description or '',
            'keywords': p.get_keywords(),
            'created_at': p.created_at.strftime('%Y-%m-%d'),
        })
    import json
    return render(request, 'position_list.html', {
        'positions': positions,
        'positions_json': json.dumps(positions_data)
    })


@csrf_exempt
@require_http_methods(["POST"])
def apply_position(request, position_id):
    """公开投递简历接口"""
    try:
        position = JobPosition.objects.get(id=position_id)
    except JobPosition.DoesNotExist:
        return JsonResponse({'success': False, 'error': '职位不存在'})

    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')

    if not request.FILES.get('resume'):
        return JsonResponse({'success': False, 'error': '请上传简历文件'})

    resume_file = request.FILES['resume']
    file_path = os.path.join(settings.MEDIA_ROOT, 'resumes', resume_file.name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        for chunk in resume_file.chunks():
            f.write(chunk)

    parser = ResumeParser()
    try:
        raw_text = parser.extract_text_from_file(file_path)
        fields = parser.extract_fields(raw_text)
        screener = ResumeScreener(position.get_keywords())
        score, matched = screener.calculate_score(raw_text)

        resume = Resume.objects.create(
            name=name or fields['name'] or resume_file.name.replace('.pdf', '').replace('.docx', '').replace('_', ' ').replace('-', ' ').title(),
            email=email or fields['email'],
            phone=phone or fields['phone'],
            education=fields['education'],
            skills=', '.join(matched),
            raw_text=raw_text[:2000],
            file=resume_file,
            score=score,
            matched_keywords=json.dumps(matched),
            position=position,
            status='passed' if score >= 60 else 'pending',
        )

        return JsonResponse({
            'success': True,
            'name': resume.name,
            'score': resume.score,
            'matched_keywords': matched,
            'email': resume.email,
            'phone': resume.phone,
            'education': resume.education,
            'status': resume.status,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def upload_resume(request, position_id):
    """上传简历并筛选（供用户端使用）"""
    position = JobPosition.objects.get(id=position_id)
    
    if request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        file_path = os.path.join(settings.MEDIA_ROOT, 'resumes', resume_file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in resume_file.chunks():
                f.write(chunk)
        
        parser = ResumeParser()
        try:
            raw_text = parser.extract_text_from_file(file_path)
            fields = parser.extract_fields(raw_text)
            screener = ResumeScreener(position.get_keywords())
            score, matched = screener.calculate_score(raw_text)
            
            resume = Resume.objects.create(
                name=fields['name'] or resume_file.name.replace('.pdf', '').replace('.docx', '').replace('_', ' ').replace('-', ' ').title(),
                email=fields['email'],
                phone=fields['phone'],
                education=fields['education'],
                skills=', '.join(matched),
                raw_text=raw_text[:2000],
                file=resume_file,
                score=score,
                matched_keywords=json.dumps(matched),
                position=position,
                status='passed' if score >= 60 else 'pending',
            )
            
            return JsonResponse({
                'success': True,
                'resume': {
                    'name': resume.name,
                    'score': resume.score,
                    'matched_keywords': matched,
                    'email': resume.email,
                    'phone': resume.phone,
                    'education': resume.education,
                    'status': resume.status,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '没有上传文件'})
