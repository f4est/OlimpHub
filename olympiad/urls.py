from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.OlympiadListView.as_view(), name='index'),
    path('olympiad/<int:pk>/', views.OlympiadDetailView.as_view(), name='olymp_detail'),
    path('olympiad/<int:pk>/tasks/', views.TasksView.as_view(), name='tasks'),
    path('olympiad/<int:pk>/scoreboard/', views.ScoreboardView.as_view(), name='scoreboard'),
    path('olympiad/create/', views.OlympiadCreateView.as_view(), name='olymp_create'),
    path('olympiad/<int:pk>/edit/', views.OlympiadUpdateView.as_view(), name='olymp_edit'),
    path('submit/<int:problem_id>/', views.submit_solution, name='submit'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    
    # Пути для работы с заданиями
    path('olympiad/<int:olympiad_id>/problem/create/', views.ProblemCreateView.as_view(), name='problem_create'),
    path('problem/<int:pk>/edit/', views.ProblemUpdateView.as_view(), name='problem_update'),
    path('problem/<int:pk>/delete/', views.ProblemDeleteView.as_view(), name='problem_delete'),
    
    # Административные маршруты (изменён префикс с admin на management)
    path('management/users/', views.UserListView.as_view(), name='user_list'),
    path('management/users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('management/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    
    # Новая админ-панель и управление статусами соревнований
    path('management-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('management-dashboard/update-statuses/', views.update_olympiad_statuses, name='update_olympiad_statuses'),
    
    # Административная панель с графиками и статистикой
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_stats_dashboard'),
    path('api/dashboard-stats/', views.get_dashboard_stats, name='dashboard_stats_api'),
    
    # API для автоматического обновления статусов
    path('api/auto-update-statuses/', views.auto_update_olympiad_statuses, name='auto_update_statuses'),
]

# Добавление настроек медиа-файлов для режима разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
