# resumes/admin.py
from django.contrib import admin
from .models import JobPosition, Resume


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'requirements')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'score', 'status', 'created_at')
    list_filter = ('status', 'position', 'created_at')
    search_fields = ('name', 'email', 'skills')
    ordering = ('-score',)
