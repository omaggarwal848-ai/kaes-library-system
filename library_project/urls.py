"""
URL configuration for kaes Library Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'profile', None) and request.user.profile.is_student:
            return redirect('student_dashboard')
        return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('students/', include('students.urls')),
    path('transactions/', include('transactions.urls')),
    path('returns-stack/', include('returns_stack.urls')),
    path('requests-queue/', include('requests_queue.urls')),
    path('csv-manager/', include('csv_manager.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
