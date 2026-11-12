from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Book, Category
from .forms import BookForm, CategoryForm
from transactions.models import ActivityLog
from requests_queue.models import BookRequest

@login_required
def book_list_view(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    availability = request.GET.get('availability', '')
    sort_by = request.GET.get('sort', 'title')

    books = Book.objects.all().select_related('category')

    # Search
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(category__name__icontains=query) |
            Q(shelf_location__icontains=query)
        )

    # Filter Category
    if category_id:
        books = books.filter(category_id=category_id)

    # Filter Availability
    if availability == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability == 'out_of_stock':
        books = books.filter(available_copies=0)

    # Sorting
    valid_sorts = {
        'title': 'title',
        '-title': '-title',
        'author': 'author',
        '-author': '-author',
        'year': '-publication_year',
        'available': '-available_copies',
        '-created': '-created_at'
    }
    books = books.order_by(valid_sorts.get(sort_by, 'title'))

    # Pagination
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'books': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_availability': availability,
        'selected_sort': sort_by,
        'total_results': paginator.count,
    }
    return render(request, 'books.html', context)


@login_required
def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    active_issues = book.issues.filter(status='issued').select_to_dict = book.issues.filter(status='issued')
    pending_holds = book.hold_requests.filter(status='pending')
    
    return render(request, 'book_detail.html', {
        'book': book,
        'active_issues': active_issues,
        'pending_holds': pending_holds,
    })


@login_required
def book_create_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Only librarians and administrators can add books.")
        return redirect('books_list')

    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        ActivityLog.objects.create(
            user=request.user,
            action_type='BOOK_ADDED',
            description=f"Added book '{book.title}' (ISBN: {book.isbn}, Copies: {book.total_copies})."
        )
        messages.success(request, f"Book '{book.title}' was added to the library catalog successfully!")
        return redirect('books_list')

    return render(request, 'book_form.html', {'form': form, 'title': 'Add New Book'})


@login_required
def book_edit_view(request, pk):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Only librarians and administrators can edit books.")
        return redirect('books_list')

    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        ActivityLog.objects.create(
            user=request.user,
            action_type='BOOK_UPDATED',
            description=f"Updated details for book '{book.title}' (ISBN: {book.isbn})."
        )
        messages.success(request, f"Book '{book.title}' updated successfully.")
        return redirect('books_list')

    return render(request, 'book_form.html', {'form': form, 'title': f'Edit Book: {book.title}', 'book': book})


@login_required
def book_delete_view(request, pk):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Only librarians and administrators can delete books.")
        return redirect('books_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        ActivityLog.objects.create(
            user=request.user,
            action_type='BOOK_DELETED',
            description=f"Deleted book '{title}' from catalog."
        )
        messages.success(request, f"Book '{title}' was deleted successfully.")
        return redirect('books_list')

    return render(request, 'confirm_delete.html', {
        'object_name': f"Book: {book.title} ({book.isbn})",
        'cancel_url': 'books_list'
    })


@login_required
def api_books_search(request):
    term = request.GET.get('q', '').strip()
    available_only = request.GET.get('available', 'false').lower() == 'true'

    books = Book.objects.all()
    if available_only:
        books = books.filter(available_copies__gt=0)
    
    if term:
        books = books.filter(
            Q(title__icontains=term) |
            Q(author__icontains=term) |
            Q(isbn__icontains=term)
        )

    results = []
    for b in books[:15]:
        results.append({
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'isbn': b.isbn,
            'available_copies': b.available_copies,
            'shelf_location': b.shelf_location,
        })
    return JsonResponse({'results': results})
