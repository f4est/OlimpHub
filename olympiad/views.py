from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DurationField
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.core.exceptions import PermissionDenied

from .models import Olympiad, Enrollment, Problem, UserProfile
from .forms import SignUpForm, UserProfileForm, OlympiadForm, ProblemForm
from submissions.forms import SubmissionForm
from submissions.models import Submission


# ────────────────────── Миксин для проверки роли ──────────────────────
class TeacherRequiredMixin(LoginRequiredMixin):
    """Миксин для проверки, что пользователь является преподавателем или администратором"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not (request.user.profile.is_teacher or request.user.profile.is_admin):
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(LoginRequiredMixin):
    """Миксин для проверки, что пользователь является администратором"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

# ────────────────────── Управление пользователями (Админ) ────────────────────────
class UserListView(AdminRequiredMixin, ListView):
    """Отображает список всех пользователей для администратора"""
    model = User
    template_name = 'admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        
        # Фильтрация по роли
        role = self.request.GET.get('role')
        if role in [UserProfile.STUDENT, UserProfile.TEACHER, UserProfile.ADMIN]:
            qs = qs.filter(profile__role=role)
        
        # Поиск по имени или email
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q)
            
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['role_filter'] = self.request.GET.get('role', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['role_choices'] = UserProfile.ROLE_CHOICES
        return ctx

class UserCreateView(AdminRequiredMixin, CreateView):
    """Позволяет администратору создавать новых пользователей"""
    model = User
    template_name = 'admin/user_form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'profile_form' not in ctx:
            ctx['profile_form'] = UserProfileForm()
        return ctx
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            return self.form_valid(form, profile_form)
        else:
            return self.form_invalid(form, profile_form)
    
    def form_valid(self, form, profile_form):
        user = form.save()
        profile = user.profile
        profile.role = profile_form.cleaned_data['role']
        profile.bio = profile_form.cleaned_data['bio']
        profile.save()
        
        messages.success(self.request, f"Пользователь {user.username} успешно создан!")
        return redirect(self.success_url)
    
    def form_invalid(self, form, profile_form):
        return self.render_to_response(
            self.get_context_data(form=form, profile_form=profile_form)
        )

class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Позволяет администратору редактировать существующих пользователей"""
    model = User
    template_name = 'admin/user_form.html'
    fields = ['username', 'email', 'is_active']
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'profile_form' not in ctx:
            ctx['profile_form'] = UserProfileForm(instance=self.object.profile)
        return ctx
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        profile_form = UserProfileForm(request.POST, instance=self.object.profile)
        
        if form.is_valid() and profile_form.is_valid():
            return self.form_valid(form, profile_form)
        else:
            return self.form_invalid(form, profile_form)
    
    def form_valid(self, form, profile_form):
        user = form.save()
        profile_form.save()
        
        messages.success(self.request, f"Пользователь {user.username} успешно обновлен!")
        return redirect(self.success_url)
    
    def form_invalid(self, form, profile_form):
        return self.render_to_response(
            self.get_context_data(form=form, profile_form=profile_form)
        )

# ────────────────────── регистрация пользователя ──────────────────────
class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = '/profile/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


# ────────────────────── профиль пользователя ──────────────────────
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)


# ────────────────────── список олимпиад ──────────────────────
class OlympiadListView(ListView):
    model = Olympiad
    template_name = 'index.html'
    context_object_name = 'olympiads'
    paginate_by = 30  # Отображаем по 30 соревнований на странице

    STATUS_TABS = [
        ('all', 'Все'),
        ('active', 'Активные'),
        ('upcoming', 'Предстоящие'),
        ('closed', 'Завершённые'),
    ]
    
    SORT_OPTIONS = [
        ('popularity', 'По популярности'),
        ('newest', 'Сначала новые'),
        ('oldest', 'Сначала старые'),
        ('duration', 'По длительности'),
        ('random', 'Случайные')
    ]

    def get_queryset(self):
        """
        Возвращает отфильтрованный и отсортированный список олимпиад
        """
        queryset = Olympiad.objects.all()
        
        # Базовая аннотация для всех запросов
        queryset = queryset.annotate(
            duration=ExpressionWrapper(
                F('end_at') - F('start_at'), 
                output_field=DurationField()
            ),
            participants_count=Count('enrollment')
        )
        
        # Получаем параметры запроса
        status = self.request.GET.get('status', 'all')
        q = self.request.GET.get('q', '')
        sort = self.request.GET.get('sort', 'popularity')
        subject = self.request.GET.get('subject', '')
        difficulty = self.request.GET.get('difficulty', '')
        my_olympiads = self.request.GET.get('my', False)
        
        # Фильтрация по параметрам
        now = timezone.now()
        
        # Устанавливаем фильтрацию в зависимости от статуса
        # Если статус "active", всегда показываем только активные соревнования
        if status == 'active':
            queryset = queryset.filter(start_at__lte=now, end_at__gte=now)
        elif status == 'upcoming':
            queryset = queryset.filter(start_at__gt=now)
        elif status == 'closed':
            queryset = queryset.filter(end_at__lt=now)
        # В режиме "all" тоже показываем только активные соревнования по умолчанию
        elif status == 'all':
            queryset = queryset.filter(start_at__lte=now, end_at__gte=now)
        
        # Поиск по тексту
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(subject__icontains=q) | 
                Q(description__icontains=q)
            )
        
        # Фильтр по предмету
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Фильтр по сложности
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Фильтр "Мои соревнования" для преподавателей
        if my_olympiads and self.request.user.is_authenticated:
            user_profile = self.request.user.userprofile
            if user_profile.role == 'teacher':
                queryset = queryset.filter(creator=self.request.user)
        
        # Сортировка результатов
        if sort == 'popularity':
            queryset = queryset.order_by('-participants_count')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'duration':
            queryset = queryset.order_by('duration')
        elif sort == 'random':
            queryset = queryset.order_by('?')
        
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_tabs'] = self.STATUS_TABS
        ctx['sort_options'] = self.SORT_OPTIONS
        
        # Текущие настройки фильтрации и сортировки
        ctx['current_status'] = self.request.GET.get('status', 'all')
        ctx['current_sort'] = self.request.GET.get('sort', 'popularity')
        ctx['current_subject'] = self.request.GET.get('subject', '')
        ctx['current_difficulty'] = self.request.GET.get('difficulty', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['show_my'] = self.request.GET.get('my') == '1'
        
        # Уникальные предметы и сложности для фильтров
        ctx['available_subjects'] = Olympiad.objects.values_list('subject', flat=True).distinct().exclude(subject='')
        ctx['difficulty_choices'] = [
            ('easy', 'Легкий'),
            ('medium', 'Средний'),
            ('hard', 'Сложный')
        ]
        
        # Статистика по всей системе
        ctx['participants_count'] = Enrollment.objects.count()
        ctx['submissions_count'] = Submission.objects.count()
        
        # Счетчики для каждого статуса
        ctx['upcoming_count'] = Olympiad.objects.filter(status=Olympiad.UPCOMING).count()
        ctx['active_count'] = Olympiad.objects.filter(status=Olympiad.ACTIVE).count()
        ctx['closed_count'] = Olympiad.objects.filter(status=Olympiad.CLOSED).count()
        
        return ctx


# ────────────────────── создание олимпиады ──────────────────────
class OlympiadCreateView(TeacherRequiredMixin, CreateView):
    model = Olympiad
    form_class = OlympiadForm
    template_name = 'olympiad_form.html'
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, "Соревнование успешно создано!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('olymp_detail', kwargs={'pk': self.object.pk})


# ────────────────────── редактирование олимпиады ──────────────────────
class OlympiadUpdateView(TeacherRequiredMixin, UpdateView):
    model = Olympiad
    form_class = OlympiadForm
    template_name = 'olympiad_form.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверка прав: только создатель или админ может редактировать
        if obj.creator != self.request.user and not self.request.user.profile.is_admin:
            raise HttpResponseForbidden("У вас нет прав для редактирования этого соревнования.")
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, "Соревнование успешно обновлено!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('olymp_detail', kwargs={'pk': self.object.pk})


# ────────────────────── страница олимпиады ──────────────────────
class OlympiadDetailView(DetailView):
    model = Olympiad
    template_name = 'olympiad_detail.html'
    context_object_name = 'olymp'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        olymp = self.object
        
        # Обновляем статус соревнования
        olymp.update_status()
        
        # Проверяем, зарегистрирован ли пользователь
        is_reg = False
        if self.request.user.is_authenticated:
            is_reg = olymp.enrollment_set.filter(user=self.request.user).exists()
        
        ctx['is_registered'] = is_reg
        ctx['participants'] = olymp.participants
        
        # Определяем, может ли пользователь зарегистрироваться (только студенты)
        can_register = False
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'profile') and self.request.user.profile.is_student:
                can_register = True
        
        ctx['can_register'] = can_register
        
        # Вычисляем продолжительность соревнования
        duration = olymp.end_at - olymp.start_at
        ctx['duration_hours'] = duration.seconds // 3600
        ctx['duration_minutes'] = (duration.seconds % 3600) // 60
        
        return ctx

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        olymp = self.get_object()
        
        # Проверяем, является ли пользователь студентом
        if not hasattr(request.user, 'profile') or not request.user.profile.is_student:
            messages.error(request, "Только студенты могут регистрироваться на соревнования.")
            return redirect('olymp_detail', pk=olymp.pk)
        
        Enrollment.objects.get_or_create(user=request.user, olympiad=olymp)
        messages.success(request, f"Вы успешно зарегистрировались на соревнование '{olymp.title}'!")
        return redirect('tasks', pk=olymp.pk)


# ────────────────────── задачи ──────────────────────
class TasksView(LoginRequiredMixin, View):
    template_name = 'tasks.html'
    
    def get(self, request, pk):
        olymp = get_object_or_404(Olympiad, pk=pk)
        olymp.update_status()  # Обновление статуса соревнования
        problems = Problem.objects.filter(olympiad=olymp)
        
        # Проверка на регистрацию
        try:
            enrollment = Enrollment.objects.get(user=request.user, olympiad=olymp)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            enrollment = None
            is_enrolled = False
        
        # Получение решений для каждой задачи
        problem_data = []
        for prob in problems:
            submissions = []
            if enrollment:
                submissions = Submission.objects.filter(
                    enrollment=enrollment,
                    problem=prob
                ).order_by('-submitted_at')  # Изменено с created_at на submitted_at
            
            problem_data.append({
                'problem': prob,
                'submissions': submissions,
                'best_submission': submissions.first() if submissions else None
            })
        
        context = {
            'olympiad': olymp,
            'problem_data': problem_data,
            'is_enrolled': is_enrolled,
            'is_teacher': hasattr(request.user, 'profile') and request.user.profile.is_teacher,
            'is_admin': hasattr(request.user, 'profile') and request.user.profile.is_admin,
            'is_creator': olymp.creator == request.user,
        }
        return render(request, self.template_name, context)


# ────────────────────── отправка решения ──────────────────────
@require_POST
@login_required
def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    
    # Проверяем, активно ли соревнование
    if problem.olympiad.status != Olympiad.ACTIVE:
        messages.error(request, "Невозможно отправить решение: соревнование не активно.")
        return redirect('tasks', pk=problem.olympiad.pk)
    
    form = SubmissionForm(request.POST, request.FILES)
    if form.is_valid():
        enrollment, _ = Enrollment.objects.get_or_create(
            user=request.user, olympiad=problem.olympiad
        )
        submission = Submission.objects.create(
            enrollment=enrollment,
            problem=problem,
            file=form.cleaned_data['file'],
        )
        messages.success(request, "Решение успешно отправлено на проверку!")
    else:
        messages.error(request, "Ошибка при отправке решения. Проверьте формат файла.")
        
    return redirect('tasks', pk=problem.olympiad.pk)


# ────────────────────── табло результатов ──────────────────────
class ScoreboardView(TemplateView):
    template_name = 'scoreboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        olymp = get_object_or_404(Olympiad, pk=kwargs['pk'])
        
        # Получаем все задачи олимпиады
        problems = olymp.problems.all()
        
        # Получаем все отправки по олимпиаде и группируем их по пользователям
        enrollments = Enrollment.objects.filter(olympiad=olymp).select_related('user')
        
        results = []
        for enrollment in enrollments:
            # Рассчитываем баллы для каждого задания
            problem_scores = []
            total_score = 0
            
            for problem in problems:
                # Находим лучшую отправку по данной задаче
                best_submission = Submission.objects.filter(
                    enrollment=enrollment,
                    problem=problem
                ).order_by('-score').first()
                
                score = best_submission.score if best_submission and best_submission.score else 0
                problem_scores.append(score)
                total_score += score
            
            results.append({
                'user': enrollment.user.username,
                'user_id': enrollment.user.id,
                'problem_scores': problem_scores,
                'total': total_score
            })
        
        # Сортируем по общему баллу
        results = sorted(results, key=lambda x: x['total'], reverse=True)
        
        ctx['olymp'] = olymp
        ctx['results'] = results
        ctx['problems'] = problems
        return ctx


# ────────────────────── профиль ──────────────────────
def medal_icon(place):
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(place, "")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Получаем регистрации пользователя
        enrolls = (
            Enrollment.objects.filter(user=user)
            .select_related('olympiad')
            .prefetch_related('submission_set')
        )
        
        rows = []
        for e in enrolls:
            olymp = e.olympiad
            total = e.submission_set.aggregate(s=Sum('score'))['s'] or 0
            
            # Вычисляем место пользователя
            standings = (
                Submission.objects.filter(enrollment__olympiad=olymp)
                .values('enrollment__user')
                .annotate(total=Sum('score'))
                .order_by('-total')
            )
            
            order = [row['enrollment__user'] for row in standings]
            place = order.index(user.id) + 1 if user.id in order else '-'
            
            rows.append({
                'olymp': olymp, 
                'total': total, 
                'place': place, 
                'medal': medal_icon(place)
            })
        
        ctx['rows'] = rows
        return ctx


# ────────────────────── создание и управление заданиями ──────────────────────
class ProblemCreateView(TeacherRequiredMixin, CreateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problem_form.html'
    
    def get_success_url(self):
        return reverse('olymp_detail', kwargs={'pk': self.kwargs['olympiad_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiad'] = get_object_or_404(Olympiad, pk=self.kwargs['olympiad_id'])
        return context
    
    def form_valid(self, form):
        olympiad = get_object_or_404(Olympiad, pk=self.kwargs['olympiad_id'])
        
        # Проверка прав: только создатель или админ может редактировать
        if olympiad.creator != self.request.user and not self.request.user.profile.is_admin:
            raise HttpResponseForbidden("У вас нет прав для добавления заданий в это соревнование.")
        
        form.instance.olympiad = olympiad
        messages.success(self.request, "Задание успешно добавлено!")
        return super().form_valid(form)

class ProblemUpdateView(TeacherRequiredMixin, UpdateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problem_form.html'
    
    def get_success_url(self):
        return reverse('olymp_detail', kwargs={'pk': self.object.olympiad.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiad'] = self.object.olympiad
        return context
    
    def form_valid(self, form):
        # Проверка прав: только создатель или админ может редактировать
        if self.object.olympiad.creator != self.request.user and not self.request.user.profile.is_admin:
            raise HttpResponseForbidden("У вас нет прав для редактирования этого задания.")
        
        messages.success(self.request, "Задание успешно обновлено!")
        return super().form_valid(form)

class ProblemDeleteView(TeacherRequiredMixin, DeleteView):
    model = Problem
    template_name = 'problem_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('olymp_detail', kwargs={'pk': self.object.olympiad.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiad'] = self.object.olympiad
        return context
    
    def delete(self, request, *args, **kwargs):
        problem = self.get_object()
        
        # Проверка прав: только создатель или админ может удалять
        if problem.olympiad.creator != self.request.user and not self.request.user.profile.is_admin:
            raise HttpResponseForbidden("У вас нет прав для удаления этого задания.")
            
        messages.success(request, f"Задание '{problem.title}' успешно удалено.")
        return super().delete(request, *args, **kwargs)

@login_required
def enroll_olympiad(request, pk):
    olymp = get_object_or_404(Olympiad, pk=pk)
    
    # Обновить статус соревнования
    olymp.update_status()
    
    # Проверка на возможность регистрации
    if olymp.status == 'completed':
        messages.error(request, "Регистрация на завершенное соревнование невозможна.")
        return redirect('olymp_detail', pk=olymp.pk)
    
    # Проверка роли пользователя (только студенты могут регистрироваться)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_student:
        messages.error(request, "Только студенты могут регистрироваться на соревнования.")
        return redirect('olymp_detail', pk=olymp.pk)
    
    # Проверка на уже существующую регистрацию
    if Enrollment.objects.filter(user=request.user, olympiad=olymp).exists():
        messages.info(request, "Вы уже зарегистрированы на это соревнование.")
        return redirect('tasks', pk=olymp.pk)
    
    # Создание записи о регистрации
    enrollment = Enrollment(user=request.user, olympiad=olymp)
    enrollment.save()
    
    messages.success(request, f"Вы успешно зарегистрировались на соревнование: {olymp.title}")
    return redirect('tasks', pk=olymp.pk)

@login_required
def admin_dashboard(request):
    """Представление для собственной панели администратора"""
    # Проверка прав администратора
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        messages.error(request, "У вас нет прав для доступа к панели администратора.")
        return redirect('index')
    
    # Получение статистики
    context = {
        'users_count': User.objects.count(),
        'olympiads_count': Olympiad.objects.count(),
        'problems_count': Problem.objects.count(),
        'submissions_count': Submission.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_olympiads': Olympiad.objects.all().order_by('-start_at')[:5],
        
        # Счетчики для каждого статуса олимпиад (для графиков)
        'upcoming_count': Olympiad.objects.filter(status=Olympiad.UPCOMING).count(),
        'active_count': Olympiad.objects.filter(status=Olympiad.ACTIVE).count(),
        'closed_count': Olympiad.objects.filter(status=Olympiad.CLOSED).count(),
        
        # Статистика по пользователям по ролям
        'student_count': UserProfile.objects.filter(role=UserProfile.STUDENT).count(),
        'teacher_count': UserProfile.objects.filter(role=UserProfile.TEACHER).count(),
        'admin_count': UserProfile.objects.filter(role=UserProfile.ADMIN).count(),
        
        # Статистика по решениям
        'pending_submissions': Submission.objects.filter(status=Submission.PENDING).count(),
        'reviewed_submissions': Submission.objects.filter(status=Submission.REVIEWED).count(),
        
        # Статистика активности за последние 7 дней
        'recent_registrations': User.objects.filter(
            date_joined__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
        'recent_enrollments': Enrollment.objects.filter(
            registered_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
        'recent_submissions': Submission.objects.filter(
            submitted_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def update_olympiad_statuses(request):
    """Обновляет статусы всех соревнований в соответствии с их датами"""
    if not request.user.profile.is_admin:
        raise PermissionDenied("Только администраторы могут выполнять это действие")
    
    olympiads = Olympiad.objects.all()
    updated_count = 0
    
    for olympiad in olympiads:
        old_status = olympiad.status
        new_status = olympiad.update_status()
        if old_status != new_status:
            updated_count += 1
    
    messages.success(request, f"Обновлены статусы {updated_count} соревнований")
    return HttpResponseRedirect(reverse('admin_stats_dashboard'))

@staff_member_required
def get_dashboard_stats(request):
    """API для получения данных для графиков на админ-панели"""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Статистика пользователей по дням за последние 7 дней
    users_stats = []
    for i in range(7):
        day = week_ago + timedelta(days=i+1)
        count = User.objects.filter(
            date_joined__date=day.date()
        ).count()
        users_stats.append({
            'day': day.strftime('%a'),  # Сокращенное название дня недели
            'count': count
        })
    
    # Статистика решений по дням за последние 7 дней
    submissions_stats = []
    for i in range(7):
        day = week_ago + timedelta(days=i+1)
        count = Submission.objects.filter(
            submitted_at__date=day.date()
        ).count()
        submissions_stats.append({
            'day': day.strftime('%a'),
            'count': count
        })
    
    # Статистика соревнований по статусу
    olympiads_stats = {
        'active': Olympiad.objects.filter(status='active').count(),
        'upcoming': Olympiad.objects.filter(status='upcoming').count(),
        'closed': Olympiad.objects.filter(status='closed').count()
    }
    
    return JsonResponse({
        'users': users_stats,
        'submissions': submissions_stats,
        'olympiads': olympiads_stats
    })

@login_required
def user_list(request):
    """Список пользователей для админа"""
    # Проверка прав администратора
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        messages.error(request, "У вас нет прав для доступа к этому разделу.")
        return redirect('index')
    
    users = User.objects.all().order_by('username')
    
    return render(request, 'user_list.html', {'users': users})

@login_required
def user_create(request):
    """Создание нового пользователя (для админа)"""
    # Проверка прав администратора
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        messages.error(request, "У вас нет прав для доступа к этому разделу.")
        return redirect('index')
    
    if request.method == 'POST':
        # Логика создания пользователя
        pass
    
    return render(request, 'user_form.html', {'form': None})

@login_required
def user_edit(request, user_id):
    """Редактирование пользователя (для админа)"""
    # Проверка прав администратора
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        messages.error(request, "У вас нет прав для доступа к этому разделу.")
        return redirect('index')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Логика обновления пользователя
        pass
    
    return render(request, 'user_form.html', {'user': user, 'form': None})

@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'admin/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Подсчет количества пользователей, соревнований, заданий и решений
        context['users_count'] = User.objects.count()
        context['olympiads_count'] = Olympiad.objects.count()
        context['problems_count'] = Problem.objects.count() 
        context['submissions_count'] = Submission.objects.count()
        
        # Подсчет количества соревнований по статусу
        context['active_olympiads'] = Olympiad.objects.filter(status='active').count()
        context['upcoming_olympiads'] = Olympiad.objects.filter(status='upcoming').count()
        context['closed_olympiads'] = Olympiad.objects.filter(status='closed').count()
        
        # Данные для графиков (можно расширить в будущем)
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)
        
        # Статистика пользователей по дням недели
        users_by_day = User.objects.filter(
            date_joined__gte=week_ago
        ).extra(
            select={'day': "date_trunc('day', date_joined)"}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Статистика решений по дням недели
        submissions_by_day = Submission.objects.filter(
            submitted_at__gte=week_ago
        ).extra(
            select={'day': "date_trunc('day', submitted_at)"}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Преобразуем результаты в формат для JavaScript
        # (в реальном приложении вы бы привели данные к формату, подходящему для графиков)
        
        return context
