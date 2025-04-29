from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from olympiad.views import ProfileView
from olympiad.admin import admin_site  # Импортируем нашу кастомную админку

urlpatterns = [
    path('admin/', admin_site.urls),  # Используем нашу кастомную админку вместо стандартной
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('accounts/profile/', ProfileView.as_view()),   # алиас
    path('', include('olympiad.urls')),
]

# Добавление настроек медиа-файлов для режима разработки
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
