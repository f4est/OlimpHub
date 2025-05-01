from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from olympiad.models import Olympiad, Problem, UserProfile
from submissions.models import Submission

class CustomAdminSite(AdminSite):
    site_header = 'OlimpHub Administration'
    site_title = 'OlimpHub Admin'
    index_title = 'Панель управления OlimpHub'
    
    def index(self, request, extra_context=None):
        """
        Переопределяем метод index, чтобы добавить информацию о статистике приложения
        """
        if extra_context is None:
            extra_context = {}
            
        # Добавляем счетчики основных моделей
        extra_context['user_count'] = User.objects.count()
        extra_context['olympiad_count'] = Olympiad.objects.count()
        extra_context['problem_count'] = Problem.objects.count()
        extra_context['submission_count'] = Submission.objects.count()
            
        return super().index(request, extra_context)

# Создаем экземпляр кастомного AdminSite
custom_admin_site = CustomAdminSite(name='admin')

# Импортируем модели и регистрируем их в кастомной админке
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from olympiad.admin import OlympiadAdmin, ProblemAdmin, UserProfileAdmin
from submissions.admin import SubmissionAdmin
from olympiad.models import Olympiad, Problem, UserProfile
from submissions.models import Submission

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Olympiad, OlympiadAdmin)
custom_admin_site.register(Problem, ProblemAdmin)
custom_admin_site.register(UserProfile, UserProfileAdmin)
custom_admin_site.register(Submission, SubmissionAdmin) 