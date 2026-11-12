from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list_view, name='books_list'),
    path('add/', views.book_create_view, name='book_add'),
    path('<int:pk>/', views.book_detail_view, name='book_detail'),
    path('<int:pk>/edit/', views.book_edit_view, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete_view, name='book_delete'),
    path('api/search/', views.api_books_search, name='api_books_search'),
]
