from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'problem', 'score', 'submitted_at')
    list_filter = ('problem__olympiad',)
    search_fields = ('enrollment__user__username',)
