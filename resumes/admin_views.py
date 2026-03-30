# resumes/admin_views.py
# Vue 管理后台 API 接口

import json
import os
import csv
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import JobPosition, Resume
from .parser import ResumeParser, ResumeScreener
from .auth_decorators import api_login_required


@csrf_exempt
@api_login_required
@require_http_methods(["GET", "POST"])
def admin_positions(request):
    """职位列表 API"""
    if request.method == 'POST':
        body = json.loads(request.body)
        p = JobPosition.objects.create(
            title=body.get('title', ''),
            requirements=body.get('requirements', ''),
            description=body.get('description', ''),
        )
        return JsonResponse({'id': p.id, 'success': True})

    positions = JobPosition.objects.all().order_by('-created_at')
    data = []
    for p in positions:
        data.append({
            'id': p.id,
            'title': p.title,
            'requirements': p.requirements,
            'description': p.description or '',
            'keywords': p.get_keywords(),
            'resume_count': p.resumes.count(),
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'positions': data})


@csrf_exempt
@api_login_required
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def admin_position_detail(request, position_id=None):
    """职位 CRUD"""
    if request.method == 'GET':
        try:
            p = JobPosition.objects.get(id=position_id)
            return JsonResponse({
                'id': p.id,
                'title': p.title,
                'requirements': p.requirements,
                'description': p.description or '',
                'keywords': p.get_keywords(),
                'resume_count': p.resumes.count(),
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        except JobPosition.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

    elif request.method == 'DELETE':
        try:
            p = JobPosition.objects.get(id=position_id)
            p.delete()
            return JsonResponse({'success': True})
        except JobPosition.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

    else:  # POST/PUT/PATCH
        body = json.loads(request.body)
        if request.method in ['PUT', 'PATCH']:
            try:
                p = JobPosition.objects.get(id=position_id)
                if 'title' in body: p.title = body['title']
                if 'requirements' in body: p.requirements = body['requirements']
                if 'description' in body: p.description = body['description']
                p.save()
                return JsonResponse({'success': True})
            except JobPosition.DoesNotExist:
                return JsonResponse({'error': 'not found'}, status=404)
        else:  # POST - create
            p = JobPosition.objects.create(
                title=body.get('title', ''),
                requirements=body.get('requirements', ''),
                description=body.get('description', ''),
            )
            return JsonResponse({'id': p.id, 'success': True})


@api_login_required
def admin_resumes(request):
    """简历列表 API"""
    resumes = Resume.objects.select_related('position').all().order_by('-created_at')
    data = []
    for r in resumes:
        data.append({
            'id': r.id,
            'name': r.name,
            'email': r.email or '',
            'phone': r.phone or '',
            'education': r.education or '',
            'skills': r.skills or '',
            'score': float(r.score),
            'status': r.status,
            'position_id': r.position_id,
            'position_title': r.position.title if r.position else '',
            'raw_text': r.raw_text or '',
            'file': r.file.name if r.file else '',
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'resumes': data})


@csrf_exempt
@api_login_required
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def admin_resume_detail(request, resume_id=None):
    """简历 CRUD"""
    if request.method == 'GET':
        try:
            r = Resume.objects.get(id=resume_id)
            return JsonResponse({
                'id': r.id, 'name': r.name, 'email': r.email or '', 'phone': r.phone or '',
                'education': r.education or '', 'skills': r.skills or '',
                'score': float(r.score), 'status': r.status,
                'position_id': r.position_id,
                'position_title': r.position.title if r.position else '',
                'raw_text': r.raw_text or '',
                'file': r.file.name if r.file else '',
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        except Resume.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

    elif request.method == 'DELETE':
        try:
            r = Resume.objects.get(id=resume_id)
            r.delete()
            return JsonResponse({'success': True})
        except Resume.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

    else:  # PATCH
        body = json.loads(request.body)
        try:
            r = Resume.objects.get(id=resume_id)
            if 'status' in body:
                r.status = body['status']
                r.save()
            return JsonResponse({'success': True})
        except Resume.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)


@csrf_exempt
@api_login_required
@require_http_methods(["POST"])
def admin_batch_upload(request):
    """批量导入简历"""
    position_id = request.POST.get('position_id')
    if not position_id:
        return JsonResponse({'error': '缺少 position_id'}, status=400)

    try:
        position = JobPosition.objects.get(id=position_id)
    except JobPosition.DoesNotExist:
        return JsonResponse({'error': '职位不存在'}, status=404)

    files = request.FILES.getlist('resumes')
    results = []
    parser = ResumeParser()
    screener = ResumeScreener(position.get_keywords())

    for resume_file in files:
        file_path = os.path.join(settings.MEDIA_ROOT, 'resumes', resume_file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in resume_file.chunks():
                f.write(chunk)

        try:
            raw_text = parser.extract_text_from_file(file_path)
            fields = parser.extract_fields(raw_text)
            score, matched = screener.calculate_score(raw_text)

            resume = Resume.objects.create(
                name=fields['name'] or resume_file.name.replace('.pdf','').replace('.docx','').replace('_',' ').replace('-',' ').title(),
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
            results.append({'name': resume.name, 'score': score, 'success': True})
        except Exception as e:
            results.append({'name': resume_file.name, 'error': str(e), 'success': False})

    return JsonResponse({'results': results})


def admin_panel(request):
    """Vue 管理后台页面"""
    return render(request, 'admin.html')


@csrf_exempt
@api_login_required
@require_http_methods(["GET"])
def admin_resume_download(request, resume_id):
    """下载简历文件"""
    resume = get_object_or_404(Resume, id=resume_id)
    if not resume.file:
        return JsonResponse({'error': '暂无简历文件'}, status=404)
    file_path = resume.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return JsonResponse({'error': '文件不存在'}, status=404)


@api_login_required
def admin_stats(request):
    """统计数据 API"""
    positions_count = JobPosition.objects.count()
    resumes_count = Resume.objects.count()
    passed_count = Resume.objects.filter(status='passed').count()
    rejected_count = Resume.objects.filter(status='rejected').count()
    pending_count = Resume.objects.filter(status='pending').count()

    resumes = Resume.objects.all()
    avg_score = sum(r.score for r in resumes) / resumes_count if resumes_count > 0 else 0

    # 分数分布
    dist = [0, 0, 0, 0, 0]
    for r in resumes:
        s = float(r.score)
        if s <= 20: dist[0] += 1
        elif s <= 40: dist[1] += 1
        elif s <= 60: dist[2] += 1
        elif s <= 80: dist[3] += 1
        else: dist[4] += 1

    # 技能关键词统计
    kw_count = {}
    for r in resumes:
        for kw in (r.skills or '').split(','):
            k = kw.strip()
            if k:
                kw_count[k] = kw_count.get(k, 0) + 1
    top_kw = sorted(kw_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return JsonResponse({
        'positions': positions_count,
        'resumes': resumes_count,
        'passed': passed_count,
        'rejected': rejected_count,
        'pending': pending_count,
        'avg_score': round(avg_score, 1),
        'score_distribution': dist,
        'top_keywords': [{'name': k, 'value': v} for k, v in top_kw],
    })


@api_login_required
def admin_export_csv(request):
    """导出简历 CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resumes.csv"'
    response.write('\ufeff'.encode('utf-8'))  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow(['姓名', '邮箱', '电话', '学历', '应聘职位', '匹配分', '状态', '匹配技能', '上传时间'])

    resumes = Resume.objects.select_related('position').all().order_by('-score')
    for r in resumes:
        writer.writerow([
            r.name,
            r.email or '',
            r.phone or '',
            r.education or '',
            r.position.title if r.position else '',
            r.score,
            {'passed': '通过', 'rejected': '淘汰', 'pending': '待定'}.get(r.status, r.status),
            r.skills or '',
            r.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response
