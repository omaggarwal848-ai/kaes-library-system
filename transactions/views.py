import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import BookIssue, BookReturn, ActivityLog
from .forms import BookIssueForm, BookReturnForm
from books.models import Book
from students.models import Student
from returns_stack.services import stack_service
from requests_queue.services import queue_service

@login_required
def issue_return_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')

    active_tab = request.GET.get('tab', 'active')
    q_search = request.GET.get('q', '').strip()

    # Active Issues
    active_issues = BookIssue.objects.filter(status='issued').select_related('book', 'student')
    if q_search:
        active_issues = active_issues.filter(
            Q(issue_id__icontains=q_search) |
            Q(book__title__icontains=q_search) |
            Q(book__isbn__icontains=q_search) |
            Q(student__student_id__icontains=q_search) |
            Q(student__first_name__icontains=q_search) |
            Q(student__last_name__icontains=q_search)
        )
    active_issues = active_issues.order_by('due_date')

    # Return History
    returns_history = BookReturn.objects.all().select_related('issue__book', 'issue__student', 'returned_to')
    if q_search:
        returns_history = returns_history.filter(
            Q(issue__issue_id__icontains=q_search) |
            Q(issue__book__title__icontains=q_search) |
            Q(issue__student__first_name__icontains=q_search)
        )
    returns_history = returns_history.order_by('-return_date')

    paginator_issues = Paginator(active_issues, 10)
    page_issues = paginator_issues.get_page(request.GET.get('page_issue'))

    paginator_returns = Paginator(returns_history, 10)
    page_returns = paginator_returns.get_page(request.GET.get('page_return'))

    issue_form = BookIssueForm()
    return_form = BookReturnForm()

    context = {
        'active_tab': active_tab,
        'q_search': q_search,
        'active_issues': page_issues,
        'returns_history': page_returns,
        'issue_form': issue_form,
        'return_form': return_form,
        'today': timezone.now().date(),
    }
    return render(request, 'issue_return.html', context)


@login_required
def issue_book_action(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            student = form.cleaned_data['student']
            issue_date = form.cleaned_data['issue_date']
            due_date = form.cleaned_data['due_date']
            notes = form.cleaned_data.get('notes', '')

            # Double check availability
            if book.available_copies <= 0:
                messages.error(request, f"Cannot issue '{book.title}': No available copies.")
                return redirect('issue_return')

            issue_id = f"ISS-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            issue = BookIssue.objects.create(
                issue_id=issue_id,
                book=book,
                student=student,
                issued_by=request.user,
                issue_date=issue_date,
                due_date=due_date,
                status='issued',
                notes=notes
            )

            # Update book availability
            book.available_copies = max(0, book.available_copies - 1)
            book.save()

            # Log Activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='BOOK_ISSUED',
                description=f"Issued book '{book.title}' to {student.full_name} ({student.student_id}). Due: {due_date}."
            )

            messages.success(request, f"Book '{book.title}' successfully issued to {student.full_name} (Issue ID: {issue_id}).")
            return redirect('issue_return')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field.capitalize()}: {err}")
    return redirect('issue_return')


@login_required
def return_book_action(request, issue_id):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    issue = get_object_or_404(BookIssue, id=issue_id, status='issued')
    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            condition = form.cleaned_data['book_condition']
            fine_collected = form.cleaned_data.get('fine_collected') or Decimal('0.00')
            remarks = form.cleaned_data.get('remarks', '')

            calculated_fine = issue.calculate_fine()
            if fine_collected > 0:
                issue.fine_amount = fine_collected
                issue.fine_paid = True
            else:
                issue.fine_amount = calculated_fine

            issue.status = 'returned'
            issue.return_date = timezone.now().date()
            issue.save()

            # Record Return
            return_record = BookReturn.objects.create(
                issue=issue,
                returned_to=request.user,
                book_condition=condition,
                fine_collected=fine_collected,
                remarks=remarks
            )

            # Increment available book copies
            book = issue.book
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save()

            # PUSH TO RETURN STACK (Manual Python Stack)
            stack_service.push(return_record, user=request.user)

            # CHECK FIFO QUEUE FOR WAITING STUDENTS
            notified_request = queue_service.notify_if_book_available(book)
            queue_msg = ""
            if notified_request:
                queue_msg = f" Student {notified_request.student.full_name} in Request Queue has been prioritized & notified!"

            # Log Activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='BOOK_RETURNED',
                description=f"Returned book '{book.title}' from {issue.student.full_name}. Pushed to Return Stack.{queue_msg}"
            )

            messages.success(request, f"Book '{book.title}' returned successfully and placed onto LIFO Return Stack!{queue_msg}")
            return redirect('issue_return')
    
    return redirect('issue_return')


@login_required
def mark_fine_paid_action(request, issue_id):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    issue = get_object_or_404(BookIssue, id=issue_id)
    issue.fine_paid = True
    issue.save()
    messages.success(request, f"Fine for issue {issue.issue_id} marked as paid.")
    return redirect('issue_return')
