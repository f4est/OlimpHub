from django.contrib import admin
from .models import Olympiad, Enrollment, Problem

@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'start_at', 'end_at', 'status')
    list_filter = ('status',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'olympiad', 'registered_at')
    search_fields = ('user__username',)

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'olympiad', 'max_score')
    list_filter = ('olympiad',)
