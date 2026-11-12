from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
]
