from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from .models import Olympiad, Enrollment, Problem
from .forms import SignUpForm
from submissions.forms import SubmissionForm
from submissions.models import Submission


# ────────────────────── регистрация пользователя ──────────────────────
class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = '/profile/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


# ────────────────────── список олимпиад ──────────────────────
# olympiad/views.py
class OlympiadListView(ListView):
    model = Olympiad
    template_name = 'index.html'
    context_object_name = 'olympiads'

    STATUS_TABS = [
        ('all', 'All'),
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    def get_queryset(self):
        qs = Olympiad.objects.order_by('-start_at')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(subject__icontains=q)
        status = self.request.GET.get('status')
        if status in dict(Olympiad.STATUS_CHOICES):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_tabs'] = self.STATUS_TABS          # ← список для шаблона
        ctx['current_status'] = self.request.GET.get('status', 'all')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


# ────────────────────── страница олимпиады ──────────────────────
class OlympiadDetailView(LoginRequiredMixin, DetailView):
    model = Olympiad
    template_name = 'olympiad_detail.html'
    context_object_name = 'olymp'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        olymp = self.object
        is_reg = olymp.enrollment_set.filter(user=self.request.user).exists()
        ctx['is_registered'] = is_reg
        return ctx

    def post(self, request, *args, **kwargs):
        olymp = self.get_object()
        Enrollment.objects.get_or_create(user=request.user, olympiad=olymp)
        return redirect('tasks', pk=olymp.pk)


# ────────────────────── задачи ──────────────────────
class TasksView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        olymp = get_object_or_404(Olympiad, pk=kwargs['pk'])
        Enrollment.objects.get_or_create(user=self.request.user, olympiad=olymp)
        ctx['olymp'] = olymp
        ctx['problems'] = olymp.problems.all()
        return ctx


# ────────────────────── отправка решения ──────────────────────
@require_POST
@login_required
def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    form = SubmissionForm(request.POST, request.FILES)
    if form.is_valid():
        enrollment, _ = Enrollment.objects.get_or_create(
            user=request.user, olympiad=problem.olympiad
        )
        Submission.objects.create(
            enrollment=enrollment,
            problem=problem,
            file=form.cleaned_data['file'],
        )
    return redirect('tasks', pk=problem.olympiad.pk)


# ────────────────────── табло результатов ──────────────────────
class ScoreboardView(TemplateView):
    template_name = 'scoreboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        olymp = get_object_or_404(Olympiad, pk=kwargs['pk'])
        results = (
            Enrollment.objects.filter(olympiad=olymp)
            .select_related('user')
            .annotate(total=Sum('submission__score'))
            .order_by('-total')
        )
        ctx['olymp'] = olymp
        ctx['results'] = results
        return ctx


# ────────────────────── профиль ──────────────────────
def medal_icon(place):
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(place, "")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        enrolls = (
            Enrollment.objects.filter(user=user)
            .select_related('olympiad')
            .prefetch_related('submission_set')
        )
        rows = []
        for e in enrolls:
            olymp = e.olympiad
            total = e.submission_set.aggregate(s=Sum('score'))['s'] or 0
            standings = (
                Submission.objects.filter(enrollment__olympiad=olymp)
                .values('enrollment__user')
                .annotate(total=Sum('score'))
                .order_by('-total')
            )
            order = [row['enrollment__user'] for row in standings]
            place = order.index(user.id) + 1 if user.id in order else '-'
            rows.append(
                {'olymp': olymp, 'total': total, 'place': place, 'medal': medal_icon(place)}
            )
        ctx['rows'] = rows
        return ctx
