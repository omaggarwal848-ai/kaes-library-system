from django.urls import path
from . import views

urlpatterns = [
    path('', views.csv_manager_view, name='csv_manager'),
    path('import/books/', views.import_books_action, name='import_books_action'),
    path('import/students/', views.import_students_action, name='import_students_action'),
    path('export/books/', views.export_books_action, name='export_books_action'),
    path('export/students/', views.export_students_action, name='export_students_action'),
    path('export/issued/', views.export_issued_action, name='export_issued_action'),
    path('export/returned/', views.export_returned_action, name='export_returned_action'),
    path('export/requests/', views.export_requests_action, name='export_requests_action'),
    path('sample/books/', views.download_sample_books, name='download_sample_books'),
    path('sample/students/', views.download_sample_students, name='download_sample_students'),
]
