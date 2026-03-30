#!/usr/bin/env python3
"""
demo.py - 简历筛选核心算法演示

不依赖 Django，直接测试简历解析和 TF-IDF 匹配算法
"""

import sys
sys.path.insert(0, '/Users/carlos/.openclaw/workspace/resume-screener')

from resumes.parser import ResumeParser, ResumeScreener

# 测试用简历文本
SAMPLE_RESUME = """
[NAME]
电话: [PHONE]
邮箱: [PHONE]@163.com

教育背景：
上海开放大学 - 软件工程专业（本科在读）

技能特长：
- Python 编程
- Django Web 开发
- MySQL 数据库
- JavaScript 基础
- Git 版本控制
- Linux 基础操作

项目经验：
1. 校园社团管理系统
   使用 Django + Vue.js 开发，实现了用户管理、活动发布等功能

2. 个人博客系统
   使用 Flask 框架开发，支持 Markdown 文章编辑

自我评价：
热爱编程，善于学习新技术，有良好的代码编写习惯。
"""

# 测试用职位关键词
JOB_KEYWORDS = [
    'Python', 'Django', 'Flask', 'MySQL', 'PostgreSQL',
    'JavaScript', 'Vue.js', 'React', 'Git', 'Linux',
    'RESTful API', 'Docker', 'Redis'
]


def main():
    print("=" * 60)
    print("智能简历筛选系统 - 算法演示")
    print("=" * 60)
    
    # 1. 解析简历
    print("\n📄 简历解析结果：")
    print("-" * 40)
    
    parser = ResumeParser()
    fields = parser.extract_fields(SAMPLE_RESUME)
    
    print(f"姓名: {fields['name']}")
    print(f"邮箱: {fields['email']}")
    print(f"电话: {fields['phone']}")
    print(f"学历: {fields['education']}")
    
    # 2. 筛选评分
    print("\n🎯 职位匹配分析：")
    print("-" * 40)
    print(f"职位关键词: {', '.join(JOB_KEYWORDS)}")
    
    screener = ResumeScreener(JOB_KEYWORDS)
    score, matched = screener.calculate_score(SAMPLE_RESUME)
    
    print(f"\n匹配分数: {score}/100")
    print(f"匹配的技能: {', '.join(matched) if matched else '无'}")
    
    # 3. 评分等级
    print("\n📊 推荐等级：", end="")
    if score >= 70:
        print("🟢 强烈推荐")
    elif score >= 40:
        print("🟡 一般匹配")
    else:
        print("🔴 不匹配")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
