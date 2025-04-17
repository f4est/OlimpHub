from django.urls import path
from . import views

urlpatterns = [
    path('', views.OlympiadListView.as_view(), name='index'),
    path('olympiad/<int:pk>/', views.OlympiadDetailView.as_view(), name='olymp_detail'),
    path('olympiad/<int:pk>/tasks/', views.TasksView.as_view(), name='tasks'),
    path('olympiad/<int:pk>/scoreboard/', views.ScoreboardView.as_view(), name='scoreboard'),
    path('submit/<int:problem_id>/', views.submit_solution, name='submit'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
]
