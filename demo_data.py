#!/usr/bin/env python3
"""
demo_data.py - 简历筛选系统演示数据生成脚本

运行方式:
    source venv/bin/activate
    python demo_data.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'screener.settings')

import django
django.setup()

from resumes.models import JobPosition, Resume
from resumes.parser import ResumeParser, ResumeScreener

# 演示用的职位配置
POSITIONS = [
    {
        'title': 'Python 开发工程师',
        'requirements': 'Python, Django, Flask, MySQL, PostgreSQL, Git, Linux, RESTful API, Docker, Vue.js',
        'description': '负责公司后端服务开发，要求熟练掌握 Python 语言及主流框架，有Web开发经验优先。'
    },
    {
        'title': '前端开发工程师',
        'requirements': 'Vue.js, React, JavaScript, TypeScript, HTML, CSS,Webpack, Git, Node.js',
        'description': '负责公司前端页面开发，要求熟悉主流前端框架，有项目经验优先。'
    },
    {
        'title': '数据分析工程师',
        'requirements': 'Python, Pandas, NumPy, SQL, MySQL, 数据可视化, 机器学习, Excel',
        'description': '负责数据分析与挖掘，要求熟悉数据分析流程，有统计学背景优先。'
    },
]

# 演示用简历数据（直接文本，非文件）
DEMO_RESUMES = [
    {
        'name': '李明',
        'email': 'liming@163.com',
        'phone': '13800138001',
        'education': '本科 - 计算机科学与技术',
        'skills': 'Python, Django, MySQL, Git, Linux',
        'score': 85.5,
        'status': 'passed',
        'raw_text': '''李明
电话: 13800138001
邮箱: liming@163.com

教育背景：
本科 - 计算机科学与技术 - 清华大学 (2019-2023)

技能特长：
- Python 编程，熟练使用 Django、Flask 框架
- MySQL 数据库设计与优化
- Git 版本控制，Linux 服务器管理
- RESTful API 开发经验

项目经验：
1. 校园社团管理系统
   使用 Django + Vue.js 开发，实现了用户管理、活动发布等功能

2. 个人博客系统
   使用 Flask 框架开发，支持 Markdown 文章编辑

自我评价：
热爱编程，善于学习新技术，有良好的代码编写习惯。''',
        'position_idx': 0,
    },
    {
        'name': '王芳',
        'email': 'wangfang@qq.com',
        'phone': '13900139002',
        'education': '硕士 - 软件工程',
        'skills': 'Python, Flask, RESTful API, Docker',
        'score': 72.3,
        'status': 'passed',
        'raw_text': '''王芳
电话: 13900139002
邮箱: wangfang@qq.com

教育背景：
硕士 - 软件工程 - 上海交通大学 (2020-2023)

技能特长：
- Python 编程，熟悉 Flask 框架
- RESTful API 设计与开发
- Docker 容器化部署
- 敏捷开发经验

项目经验：
1. 电商后端服务
   使用 Flask 开发商品管理、订单处理等微服务

2. 数据采集系统
   使用 Python + Redis 实现高并发数据采集''',
        'position_idx': 0,
    },
    {
        'name': '张伟',
        'email': 'zhangwei@126.com',
        'phone': '13700137003',
        'education': '本科 - 信息管理',
        'skills': 'MySQL',
        'score': 35.0,
        'status': 'pending',
        'raw_text': '''张伟
电话: 13700137003
邮箱: zhangwei@126.com

教育背景：
本科 - 信息管理 - 华东理工大学 (2018-2022)

技能特长：
- MySQL 数据库基础操作
- Excel 数据处理
- 基础 HTML 知识''',
        'position_idx': 0,
    },
    {
        'name': '刘洋',
        'email': 'liuyang@outlook.com',
        'phone': '13600136001',
        'education': '本科 - 计算机科学',
        'skills': 'Vue.js, JavaScript, HTML, CSS, React',
        'score': 88.0,
        'status': 'passed',
        'raw_text': '''刘洋
电话: 13600136001
邮箱: liuyang@outlook.com

教育背景：
本科 - 计算机科学 - 浙江大学 (2019-2023)

技能特长：
- Vue.js 框架开发，2年项目经验
- JavaScript/TypeScript 熟练
- React 框架了解
- HTML5/CSS3 响应式布局
- Webpack 构建工具使用

项目经验：
1. 企业管理后台
   使用 Vue.js + Element UI 开发

2. 移动端商城
   使用 Vue.js + Vant 开发''',
        'position_idx': 1,
    },
    {
        'name': '陈静',
        'email': 'chenjing@qq.com',
        'phone': '13500135002',
        'education': '硕士 - 数据科学',
        'skills': 'Python, Pandas, NumPy, SQL, 数据可视化',
        'score': 91.5,
        'status': 'passed',
        'raw_text': '''陈静
电话: 13500135002
邮箱: chenjing@qq.com

教育背景：
硕士 - 数据科学 - 北京大学 (2020-2023)

技能特长：
- Python 编程，熟练使用 Pandas、NumPy
- SQL 查询与数据库设计
- 数据可视化（ECharts、Matplotlib）
- 机器学习基础
- Excel 高级应用

项目经验：
1. 销售数据分析平台
   使用 Python + ECharts 实现数据可视化

2. 用户行为分析
   使用机器学习进行用户聚类分析''',
        'position_idx': 2,
    },
    {
        'name': '赵强',
        'email': 'zhaoqiang@163.com',
        'phone': '13400134003',
        'education': '本科 - 统计学',
        'skills': 'Python, SQL, Excel, 数据可视化',
        'score': 65.0,
        'status': 'pending',
        'raw_text': '''赵强
电话: 13400134003
邮箱: zhaoqiang@163.com

教育背景：
本科 - 统计学 - 华东师范大学 (2018-2022)

技能特长：
- SQL 数据库查询
- Excel 数据处理与透视表
- 基础 Python 编程
- 数据可视化报告制作''',
        'position_idx': 2,
    },
]


def main():
    print("=" * 60)
    print("智能简历筛选系统 - 演示数据生成")
    print("=" * 60)

    # 清空现有数据（可选）
    print("\n📦 创建演示数据...")

    # 创建职位
    positions = []
    for pos_data in POSITIONS:
        pos, created = JobPosition.objects.get_or_create(
            title=pos_data['title'],
            defaults={
                'requirements': pos_data['requirements'],
                'description': pos_data['description'],
            }
        )
        positions.append(pos)
        action = "创建" if created else "已存在"
        print(f"  ✅ 职位: {pos.title} ({action})")

    # 创建简历
    for resume_data in DEMO_RESUMES:
        pos_idx = resume_data.pop('position_idx')
        position = positions[pos_idx]

        # 检查是否已存在同名简历
        existing = Resume.objects.filter(name=resume_data['name'], position=position).first()
        if existing:
            print(f"  ⏭️  简历 {resume_data['name']} - 已存在，跳过")
            continue

        resume = Resume.objects.create(
            name=resume_data['name'],
            email=resume_data['email'],
            phone=resume_data['phone'],
            education=resume_data['education'],
            skills=resume_data['skills'],
            raw_text=resume_data['raw_text'],
            score=resume_data['score'],
            status=resume_data['status'],
            position=position,
        )
        print(f"  ✅ 简历: {resume.name} -> {position.title} (分数: {resume.score})")

    # 统计
    print("\n📊 数据统计:")
    print(f"  - 职位总数: {JobPosition.objects.count()}")
    print(f"  - 简历总数: {Resume.objects.count()}")
    print(f"  - 通过筛选: {Resume.objects.filter(status='passed').count()}")
    print(f"  - 待定: {Resume.objects.filter(status='pending').count()}")

    print("\n" + "=" * 60)
    print("演示数据创建完成！")
    print("=" * 60)
    print("\n启动服务:")
    print("  source venv/bin/activate")
    print("  python manage.py runserver")
    print("\n访问 http://127.0.0.1:8000 查看系统")


if __name__ == '__main__':
    main()
