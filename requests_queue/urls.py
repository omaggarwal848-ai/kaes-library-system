from django.urls import path
from . import views

urlpatterns = [
    path('', views.queue_view, name='queue_view'),
    path('enqueue/', views.queue_enqueue_action, name='queue_enqueue_action'),
    path('dequeue/', views.queue_dequeue_action, name='queue_dequeue_action'),
    path('api/dequeue/', views.api_queue_dequeue, name='api_queue_dequeue'),
    path('api/peek/', views.api_queue_peek, name='api_queue_peek'),
    path('api/status/', views.api_queue_status, name='api_queue_status'),
]
