from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

from olympiad.views import (
    SignUpView, ProfileView, ProfileUpdateView,
    AboutView, ContactsView, auto_update_olympiad_statuses,
    admin_dashboard
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Авторизация
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    
    # Статические страницы
    path('about/', AboutView.as_view(), name='about'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    
    # Dashboard для админа
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # API для AJAX обновления статусов
    path('api/auto-update-statuses/', auto_update_olympiad_statuses, name='auto_update_statuses'),
    
    # Olympiad приложение
    path('', include('olympiad.urls')),
]

# Добавляем URL для обслуживания медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
