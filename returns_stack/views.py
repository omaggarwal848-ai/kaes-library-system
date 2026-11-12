from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import stack_service
from .stack_ds import StackEmptyException
from .models import ReturnStackItem
from books.models import Book
from students.models import Student
from transactions.models import BookIssue, BookReturn

@login_required
def stack_view(request):
    """
    Dedicated Stack Management UI Page.
    Displays manual Python list LIFO Stack visualization, POP/PEEK/DISPLAY operations,
    and complete return audit history.
    """
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')

    current_stack = stack_service.display()  # LIFO order: top item first
    stack_top = stack_service.peek()
    stack_size = stack_service.size()
    history = stack_service.get_history(limit=50)

    context = {
        'stack_items': current_stack,
        'stack_top': stack_top,
        'stack_size': stack_size,
        'history': history,
    }
    return render(request, 'stack.html', context)


@login_required
@require_POST
def stack_pop_action(request):
    """Pops the top item from the manual Python Stack."""
    try:
        popped_item = stack_service.pop(user=request.user)
        messages.success(request, f"LIFO POP: '{popped_item.get('book_title')}' removed from top of return stack and marked as inspected/reshelved.")
    except StackEmptyException as e:
        messages.error(request, str(e))
    return redirect('stack_view')


@login_required
def api_stack_pop(request):
    """AJAX endpoint for popping from stack with animated response."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    try:
        popped = stack_service.pop(user=request.user)
        return JsonResponse({
            'status': 'success',
            'message': f"Popped '{popped.get('book_title')}' from top of return stack.",
            'popped_item': popped,
            'new_size': stack_service.size(),
            'new_top': stack_service.peek()
        })
    except StackEmptyException as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_stack_peek(request):
    """AJAX endpoint to peek at the top item without removing it."""
    top_item = stack_service.peek()
    if top_item:
        return JsonResponse({
            'status': 'success',
            'peek_item': top_item,
            'stack_size': stack_service.size()
        })
    return JsonResponse({
        'status': 'empty',
        'message': 'Stack is currently empty. No items to peek.',
        'stack_size': 0
    })


@login_required
def api_stack_status(request):
    """Returns current stack items in LIFO order for real-time frontend rendering."""
    return JsonResponse({
        'status': 'success',
        'size': stack_service.size(),
        'items': stack_service.display(),
        'top': stack_service.peek()
    })
