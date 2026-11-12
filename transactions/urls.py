from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_return_view, name='issue_return'),
    path('issue/action/', views.issue_book_action, name='issue_book_action'),
    path('return/action/<int:issue_id>/', views.return_book_action, name='return_book_action'),
    path('fine/pay/<int:issue_id>/', views.mark_fine_paid_action, name='mark_fine_paid_action'),
]
