from django.contrib import admin
from .models import Olympiad, Enrollment, Problem, UserProfile
from submissions.models import Submission
from django.db.models import Count
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'organization')

@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'start_at', 'end_at', 'status', 'creator')
    list_filter = ('status', 'subject', 'difficulty')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'subject', 'description', 'rules', 'difficulty')
        }),
        ('Даты и статус', {
            'fields': ('start_at', 'end_at', 'status')
        }),
        ('Связи', {
            'fields': ('creator',)
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'olympiad', 'registered_at')
    list_filter = ('olympiad',)
    search_fields = ('user__username', 'olympiad__title')
    date_hierarchy = 'registered_at'

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'olympiad', 'max_score')
    list_filter = ('olympiad',)
    search_fields = ('title', 'description')

# Кастомизация админки
class CustomAdminSite(admin.AdminSite):
    site_header = 'OlimpHub Администрирование'
    site_title = 'OlimpHub Admin'
    index_title = 'Панель управления'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Подсчет количества пользователей, соревнований, заданий и решений
        context = {
            'users_count': User.objects.count(),
            'olympiads_count': Olympiad.objects.count(),
            'problems_count': Problem.objects.count(),
            'submissions_count': Submission.objects.count(),
            
            # Подсчет количества соревнований по статусу
            'active_olympiads': Olympiad.objects.filter(status='active').count(),
            'upcoming_olympiads': Olympiad.objects.filter(status='upcoming').count(),
            'closed_olympiads': Olympiad.objects.filter(status='closed').count(),
            
            # Статистика пользователей по ролям
            'student_count': UserProfile.objects.filter(role=UserProfile.STUDENT).count(),
            'teacher_count': UserProfile.objects.filter(role=UserProfile.TEACHER).count(),
            'admin_count': UserProfile.objects.filter(role=UserProfile.ADMIN).count(),
            
            # Статистика активности за последние 7 дней
            'recent_users': User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count(),
            
            'recent_enrollments': Enrollment.objects.filter(
                registered_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            
            'recent_submissions': Submission.objects.filter(
                submitted_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            
            # Данные для графиков
            'title': 'Статистика OlimpHub',
            'app_list': self.get_app_list(request),
        }
        
        return render(request, 'admin/index.html', context)

# Используем кастомную админку
admin_site = CustomAdminSite(name='admin')
admin_site.register(Olympiad, OlympiadAdmin)
admin_site.register(Problem, ProblemAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(Enrollment, EnrollmentAdmin)
admin_site.register(User)
admin_site.register(Submission)
