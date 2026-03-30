# resumes/parser.py
# 简历解析核心模块

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 可选：用于 Word 文档
try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

# 可选：用于 PDF
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class ResumeParser:
    """简历解析器 - 提取文本信息"""

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """根据文件类型提取文本"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.pdf':
            return ResumeParser._extract_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return ResumeParser._extract_docx(file_path)
        elif suffix == '.txt':
            return ResumeParser._extract_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """从 PDF 提取文本"""
        if PyPDF2 is None:
            raise ImportError("请安装 PyPDF2: pip install PyPDF2")
        try:
            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            result = '\n'.join(text)
            if not result.strip():
                # 尝试提取图片中的文字（OCR fallback）
                raise ValueError("PDF 文本为空，可能为扫描件")
            return result
        except Exception as e:
            raise ValueError(f"PDF 解析失败: {str(e)}")

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """从 Word 文档提取文本"""
        if DocxDocument is None:
            raise ImportError("请安装 python-docx: pip install python-docx")
        try:
            doc = DocxDocument(file_path)
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            result = '\n'.join(paragraphs)
            if not result.strip():
                raise ValueError("Word 文档内容为空")
            return result
        except Exception as e:
            raise ValueError(f"Word 文档解析失败: {str(e)}")

    @staticmethod
    def _extract_txt(file_path: str) -> str:
        """从 TXT 文件提取文本"""
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法解码文本文件，编码不支持")

    @staticmethod
    def safe_extract_text(file_path: str) -> str:
        """安全的文本提取，失败时返回空字符串而不抛出异常"""
        try:
            return ResumeParser.extract_text_from_file(file_path)
        except Exception:
            return ''

    @staticmethod
    def extract_fields(text: str) -> Dict[str, str]:
        """从简历文本中提取关键字段"""
        fields = {
            'name': '',
            'email': '',
            'phone': '',
            'education': '',
            'skills': '',
        }

        # 提取邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            fields['email'] = emails[0]

        # 提取手机号
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, text)
        if phones:
            fields['phone'] = phones[0]

        # 提取姓名（通常在文档开头）
        lines = text.split('\n')
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if line and len(line) < 10 and not re.search(r'[a-zA-Z0-9@]', line):
                if not any(kw in line for kw in ['简历', '个人', '求职', '姓名', '电话', '邮箱', '学历']):
                    fields['name'] = line
                    break

        # 提取学历关键词
        edu_keywords = ['博士', '硕士', '本科', '专科', '学士', '研究生', '大学', '学院', '专业']
        for line in text.split('\n'):
            for kw in edu_keywords:
                if kw in line:
                    fields['education'] = line.strip()
                    break
            if fields['education']:
                break

        return fields


class ResumeScreener:
    """简历筛选器 - TF-IDF + 关键词匹配"""

    def __init__(self, job_keywords: List[str]):
        """
        初始化筛选器
        :param job_keywords: 职位要求的关键词列表
        """
        self.job_keywords = job_keywords
        # 初始化 TF-IDF 向量化器
        self.vectorizer = TfidfVectorizer(
            tokenizer=jieba.lcut,
            lowercase=True,
            max_features=1000,
            ngram_range=(1, 2)
        )
        # 对职位关键词进行向量化
        job_text = ' '.join(job_keywords)
        self.job_vector = self.vectorizer.fit_transform([job_text])

    def calculate_score(self, resume_text: str) -> Tuple[float, List[str]]:
        """
        计算简历与职位的匹配分数
        :param resume_text: 简历文本
        :return: (分数, 匹配的关键词列表)
        """
        # 关键词匹配
        matched_keywords = []
        resume_lower = resume_text.lower()
        for keyword in self.job_keywords:
            if keyword.lower() in resume_lower:
                matched_keywords.append(keyword)

        # TF-IDF 相似度计算
        resume_vector = self.vectorizer.transform([resume_text])
        similarity = cosine_similarity(resume_vector, self.job_vector)[0][0]

        # 综合分数：关键词匹配占 60%，TF-IDF 相似度占 40%
        keyword_score = len(matched_keywords) / len(self.job_keywords) if self.job_keywords else 0
        final_score = keyword_score * 0.6 + similarity * 0.4

        # 归一化到 0-100
        final_score = min(final_score * 100, 100)

        return round(final_score, 2), matched_keywords

    def batch_screen(self, resumes: List[Dict]) -> List[Dict]:
        """
        批量筛选简历
        :param resumes: 简历列表，每项包含 text 和 name
        :return: 筛选结果列表
        """
        results = []
        for resume in resumes:
            score, matched = self.calculate_score(resume.get('text', ''))
            results.append({
                'name': resume.get('name', '未知'),
                'score': score,
                'matched_keywords': matched,
                'email': resume.get('email', ''),
                'phone': resume.get('phone', ''),
            })

        # 按分数降序排列
        results.sort(key=lambda x: x['score'], reverse=True)
        return results


def screen_resume(file_path: str, job_keywords: List[str]) -> Dict:
    """
    便捷函数：对单个简历进行筛选
    """
    parser = ResumeParser()
    screener = ResumeScreener(job_keywords)

    # 解析简历
    text = parser.extract_text_from_file(file_path)
    fields = parser.extract_fields(text)

    # 筛选
    score, matched = screener.calculate_score(text)

    return {
        'name': fields['name'],
        'email': fields['email'],
        'phone': fields['phone'],
        'education': fields['education'],
        'score': score,
        'matched_keywords': matched,
        'raw_text': text[:500],  # 保留前500字符
    }
