from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .forms import LoginForm, StudentRegistrationForm, UserProfileUpdateForm
from .models import UserProfile
from books.models import Book, Category
from students.models import Student
from transactions.models import BookIssue, BookReturn, ActivityLog
from returns_stack.services import stack_service
from requests_queue.services import queue_service

def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'profile', None) and request.user.profile.is_student:
            return redirect('student_dashboard')
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Allow logging in via email or username
        user = authenticate(request, username=username, password=password)
        if user is None:
            user_by_email = User.objects.filter(email=username).first()
            if user_by_email:
                user = authenticate(request, username=user_by_email.username, password=password)

        if user is not None:
            login(request, user)
            ActivityLog.objects.create(
                user=user,
                action_type='USER_LOGIN',
                description=f"User '{user.username}' successfully logged in."
            )
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if getattr(user, 'profile', None) and user.profile.is_student:
                return redirect('student_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action_type='USER_LOGOUT',
            description=f"User '{request.user.username}' logged out."
        )
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Create auth User
        user = User.objects.create_user(
            username=username,
            email=form.cleaned_data['email'],
            password=password,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name']
        )
        
        # UserProfile is created automatically by signal, set role to student
        profile = user.profile
        profile.role = 'student'
        profile.phone = form.cleaned_data['phone']
        profile.address = form.cleaned_data.get('address', '')
        profile.save()

        # Save student record linked to user
        student = form.save(commit=False)
        student.user = user
        student.save()

        ActivityLog.objects.create(
            user=user,
            action_type='STUDENT_ADDED',
            description=f"New student '{student.full_name}' registered ({student.student_id})."
        )

        # Log user in directly
        login(request, user)
        messages.success(request, f"Welcome to Kaes Library, {student.first_name}! Your account has been created.")
        return redirect('student_dashboard')

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard_view(request):
    # Check if student, redirect to student dashboard
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')

    # Real-time statistics
    total_books = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    available_books = Book.objects.aggregate(avail=Sum('available_copies'))['avail'] or 0
    unique_titles = Book.objects.count()
    issued_books = BookIssue.objects.filter(status='issued').count()
    total_students = Student.objects.count()
    pending_requests = queue_service.size()
    returned_books = BookReturn.objects.count()
    overdue_issues = BookIssue.objects.filter(status='issued', due_date__lt=timezone.now().date()).count()

    # Category breakdown for Chart.js
    categories = Category.objects.annotate(count=Count('books')).filter(count__gt=0)
    category_labels = [c.name for c in categories]
    category_counts = [c.count for c in categories]

    # Monthly issue & return trends for past 6 months
    today = timezone.now().date()
    months_labels = []
    monthly_issues = []
    monthly_returns = []

    for i in range(5, -1, -1):
        m_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        # Next month start
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year+1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month+1, day=1)
        
        m_name = m_start.strftime('%b %Y')
        months_labels.append(m_name)
        
        i_cnt = BookIssue.objects.filter(issue_date__gte=m_start, issue_date__lt=m_end).count()
        r_cnt = BookReturn.objects.filter(return_date__gte=m_start, return_date__lt=m_end).count()
        monthly_issues.append(i_cnt)
        monthly_returns.append(r_cnt)

    # Recent activities
    recent_activities = ActivityLog.objects.all().order_by('-created_at')[:8]

    # Latest book requests
    latest_requests = queue_service.display()[:5]

    # Stack & Queue stats
    stack_size = stack_service.size()
    stack_top = stack_service.peek()
    queue_front = queue_service.peek()

    context = {
        'total_books': total_books,
        'unique_titles': unique_titles,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_students': total_students,
        'pending_requests': pending_requests,
        'returned_books': returned_books,
        'overdue_issues': overdue_issues,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'months_labels': months_labels,
        'monthly_issues': monthly_issues,
        'monthly_returns': monthly_returns,
        'recent_activities': recent_activities,
        'latest_requests': latest_requests,
        'stack_size': stack_size,
        'stack_top': stack_top,
        'queue_front': queue_front,
    }
    return render(request, 'dashboard.html', context)


@login_required
def student_dashboard_view(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        # If user has no student record, find by email or create
        student = Student.objects.filter(email=request.user.email).first()

    my_issues = BookIssue.objects.filter(student=student, status='issued').order_by('due_date') if student else []
    my_returns = BookIssue.objects.filter(student=student, status='returned').order_by('-return_date')[:10] if student else []
    my_requests = student.book_requests.all().order_by('-request_date') if student else []

    # Available catalog recommendations
    recommended_books = Book.objects.filter(available_copies__gt=0).order_by('-created_at')[:6]

    context = {
        'student': student,
        'my_issues': my_issues,
        'my_returns': my_returns,
        'my_requests': my_requests,
        'recommended_books': recommended_books,
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile, initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email
    })

    if request.method == 'POST' and form.is_valid():
        request.user.first_name = form.cleaned_data['first_name']
        request.user.last_name = form.cleaned_data['last_name']
        request.user.email = form.cleaned_data['email']
        request.user.save()
        form.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('profile')

    return render(request, 'profile.html', {'form': form, 'profile': profile})


@login_required
def activity_logs_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Access restricted to library administrators.")
        return redirect('student_dashboard')

    action_filter = request.GET.get('action', '')
    logs = ActivityLog.objects.all().order_by('-created_at')
    if action_filter:
        logs = logs.filter(action_type=action_filter)

    return render(request, 'activity_logs.html', {
        'logs': logs[:100],
        'action_filter': action_filter,
        'action_types': ActivityLog.ACTION_TYPES
    })
