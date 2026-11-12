from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Student
from .forms import StudentForm
from transactions.models import ActivityLog, BookIssue

@login_required
def student_list_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        return redirect('student_dashboard')

    query = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    status = request.GET.get('status', '').strip()

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    if department:
        students = students.filter(department=department)

    if status:
        students = students.filter(status=status)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = [choice[0] for choice in Student.DEPARTMENT_CHOICES]

    context = {
        'students': page_obj,
        'query': query,
        'departments': departments,
        'selected_department': department,
        'selected_status': status,
        'total_results': paginator.count,
    }
    return render(request, 'students.html', context)


@login_required
def student_detail_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    active_loans = student.issues.filter(status='issued').order_by('due_date')
    history_loans = student.issues.filter(status='returned').order_by('-return_date')
    requests = student.book_requests.all().order_by('-request_date')

    return render(request, 'student_detail.html', {
        'student': student,
        'active_loans': active_loans,
        'history_loans': history_loans,
        'requests': requests,
    })


@login_required
def student_create_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save()
        ActivityLog.objects.create(
            user=request.user,
            action_type='STUDENT_ADDED',
            description=f"Admin added student record '{student.full_name}' ({student.student_id})."
        )
        messages.success(request, f"Student '{student.full_name}' was registered successfully!")
        return redirect('students_list')

    return render(request, 'student_form.html', {'form': form, 'title': 'Register New Student'})


@login_required
def student_edit_view(request, pk):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        student = form.save()
        ActivityLog.objects.create(
            user=request.user,
            action_type='STUDENT_ADDED',
            description=f"Admin updated student record for '{student.full_name}' ({student.student_id})."
        )
        messages.success(request, f"Student '{student.full_name}' updated successfully.")
        return redirect('students_list')

    return render(request, 'student_form.html', {'form': form, 'title': f'Edit Student: {student.full_name}', 'student': student})


@login_required
def student_delete_view(request, pk):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.full_name
        sid = student.student_id
        student.delete()
        ActivityLog.objects.create(
            user=request.user,
            action_type='STUDENT_ADDED',
            description=f"Admin deleted student '{name}' ({sid})."
        )
        messages.success(request, f"Student '{name}' ({sid}) was deleted.")
        return redirect('students_list')

    return render(request, 'confirm_delete.html', {
        'object_name': f"Student: {student.full_name} ({student.student_id})",
        'cancel_url': 'students_list'
    })


@login_required
def api_students_search(request):
    term = request.GET.get('q', '').strip()
    students = Student.objects.filter(status='active')
    if term:
        students = students.filter(
            Q(first_name__icontains=term) |
            Q(last_name__icontains=term) |
            Q(student_id__icontains=term) |
            Q(email__icontains=term)
        )

    results = []
    for s in students[:15]:
        results.append({
            'id': s.id,
            'name': s.full_name,
            'student_id': s.student_id,
            'email': s.email,
            'department': s.department,
            'currently_issued': s.currently_issued_count,
        })
    return JsonResponse({'results': results})
