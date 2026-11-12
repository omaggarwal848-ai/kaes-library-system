from django.urls import path
from . import views

urlpatterns = [
    path('', views.stack_view, name='stack_view'),
    path('pop/', views.stack_pop_action, name='stack_pop_action'),
    path('api/pop/', views.api_stack_pop, name='api_stack_pop'),
    path('api/peek/', views.api_stack_peek, name='api_stack_peek'),
    path('api/status/', views.api_stack_status, name='api_stack_status'),
]
