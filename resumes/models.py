from django.db import models


class JobPosition(models.Model):
    """职位表"""
    title = models.CharField('职位名称', max_length=200)
    requirements = models.TextField('职位要求（关键词，用逗号分隔）', help_text='如：Python, Django, MySQL, 3年经验')
    description = models.TextField('职位描述', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_keywords(self):
        """获取关键词列表"""
        return [k.strip() for k in self.requirements.split(',') if k.strip()]


class Resume(models.Model):
    """简历表"""
    STATUS_CHOICES = [
        ('pending', '待筛选'),
        ('passed', '通过'),
        ('rejected', '淘汰'),
    ]

    name = models.CharField('姓名', max_length=100)
    email = models.CharField('邮箱', max_length=200, blank=True)
    phone = models.CharField('电话', max_length=50, blank=True)
    education = models.CharField('学历', max_length=100, blank=True)
    skills = models.TextField('技能', blank=True, help_text='自动从简历中提取的技能')
    raw_text = models.TextField('简历原始文本', blank=True)
    file = models.FileField('简历文件', upload_to='resumes/', blank=True, null=True)
    score = models.FloatField('匹配分数', default=0.0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    matched_keywords = models.TextField('匹配的关键词', blank=True, help_text='JSON格式')
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)

    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'
        ordering = ['-score']

    def __str__(self):
        return f"{self.name} - {self.position.title if self.position else '未分配'}"
