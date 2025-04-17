from django.contrib import admin
from django.urls import path, include
from olympiad.views import ProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('accounts/profile/', ProfileView.as_view()),   # алиас
    path('', include('olympiad.urls')),
]

# +serve(media) в DEBUG при необходимости
