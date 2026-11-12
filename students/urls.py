from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list_view, name='students_list'),
    path('add/', views.student_create_view, name='student_add'),
    path('<int:pk>/', views.student_detail_view, name='student_detail'),
    path('<int:pk>/edit/', views.student_edit_view, name='student_edit'),
    path('<int:pk>/delete/', views.student_delete_view, name='student_delete'),
    path('api/search/', views.api_students_search, name='api_students_search'),
]
