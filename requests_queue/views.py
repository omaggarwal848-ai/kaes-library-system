from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import queue_service
from .queue_ds import QueueEmptyException
from .models import BookRequest
from books.models import Book
from students.models import Student

@login_required
def queue_view(request):
    """
    Dedicated Queue Management UI Page.
    Visualizes manual collections.deque FIFO Queue with Front & Rear indicators,
    DEQUEUE/PEEK/ENQUEUE operations, and processed requests log.
    """
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')

    queue_items = queue_service.display()  # FIFO order: Front to Rear
    queue_front = queue_service.peek()
    queue_rear = queue_service.peek_rear()
    queue_size = queue_service.size()
    all_requests = BookRequest.objects.all().order_by('-request_date')[:50]
    available_books = Book.objects.all().order_by('title')
    students = Student.objects.filter(status='active').order_by('first_name')

    context = {
        'queue_items': queue_items,
        'queue_front': queue_front,
        'queue_rear': queue_rear,
        'queue_size': queue_size,
        'all_requests': all_requests,
        'books': available_books,
        'students': students,
    }
    return render(request, 'queue.html', context)


@login_required
@require_POST
def queue_enqueue_action(request):
    """Adds a new book hold request to the rear of the FIFO Queue."""
    book_id = request.POST.get('book_id')
    student_id = request.POST.get('student_id')
    remarks = request.POST.get('remarks', '')

    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        # If student is enqueueing from their own dashboard
        student = Student.objects.filter(user=request.user).first() or Student.objects.filter(email=request.user.email).first()
    else:
        student = get_object_or_404(Student, id=student_id)

    book = get_object_or_404(Book, id=book_id)

    if not student:
        messages.error(request, "Student record could not be identified.")
        return redirect('queue_view')

    # Check if this student already has an active pending request for this book
    already_pending = BookRequest.objects.filter(student=student, book=book, status='pending').exists()
    if already_pending:
        messages.warning(request, f"Student {student.full_name} already has a pending request in the queue for '{book.title}'.")
        return redirect('queue_view' if not (hasattr(request.user, 'profile') and request.user.profile.is_student) else 'student_dashboard')

    req = queue_service.enqueue(student, book, remarks=remarks, user=request.user)
    messages.success(request, f"FIFO ENQUEUE: Request {req.request_id} for '{book.title}' placed at rear of Queue. Current Queue Size: {queue_service.size()}.")

    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')
    return redirect('queue_view')


@login_required
@require_POST
def queue_dequeue_action(request):
    """Processes (dequeues) the oldest pending request at the front of the queue."""
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    try:
        dequeued = queue_service.dequeue(user=request.user, status='approved')
        messages.success(request, f"FIFO DEQUEUE: Processed request {dequeued.get('request_id')} for {dequeued.get('student_name')}. Student has been notified to pick up '{dequeued.get('book_title')}'.")
    except QueueEmptyException as e:
        messages.error(request, str(e))
    return redirect('queue_view')


@login_required
def api_queue_dequeue(request):
    """AJAX endpoint for dequeuing from request queue."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    try:
        dequeued = queue_service.dequeue(user=request.user, status='approved')
        return JsonResponse({
            'status': 'success',
            'message': f"Dequeued request {dequeued.get('request_id')} for '{dequeued.get('book_title')}'. Student notified.",
            'dequeued_item': dequeued,
            'new_size': queue_service.size(),
            'new_front': queue_service.peek()
        })
    except QueueEmptyException as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_queue_peek(request):
    """AJAX endpoint to peek at front request."""
    front_item = queue_service.peek()
    if front_item:
        return JsonResponse({
            'status': 'success',
            'peek_item': front_item,
            'queue_size': queue_service.size()
        })
    return JsonResponse({
        'status': 'empty',
        'message': 'Queue is currently empty. No pending requests.',
        'queue_size': 0
    })


@login_required
def api_queue_status(request):
    """Returns all current requests in FIFO order for real-time frontend rendering."""
    return JsonResponse({
        'status': 'success',
        'size': queue_service.size(),
        'items': queue_service.display(),
        'front': queue_service.peek(),
        'rear': queue_service.peek_rear()
    })
