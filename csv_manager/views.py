import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, FileResponse

from .services import CsvService

@login_required
def csv_manager_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    return render(request, 'csv_manager.html')


@login_required
def import_books_action(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    if request.method == 'POST' and request.FILES.get('books_csv'):
        csv_file = request.FILES['books_csv']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file (.csv).")
            return redirect('csv_manager')

        report = CsvService.import_books(csv_file, user=request.user)
        request.session['books_import_report'] = report
        if report['errors'] and report['added'] == 0 and report['updated'] == 0:
            messages.error(request, f"Import Failed: {report['errors'][0]}")
        else:
            messages.success(request, f"Books CSV processed: {report['added']} added, {report['updated']} updated, {report['skipped']} skipped.")
    else:
        messages.warning(request, "No file was selected for upload.")

    return redirect('csv_manager')


@login_required
def import_students_action(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_student:
        messages.error(request, "Permission denied.")
        return redirect('student_dashboard')

    if request.method == 'POST' and request.FILES.get('students_csv'):
        csv_file = request.FILES['students_csv']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file (.csv).")
            return redirect('csv_manager')

        report = CsvService.import_students(csv_file, user=request.user)
        request.session['students_import_report'] = report
        if report['errors'] and report['added'] == 0 and report['updated'] == 0:
            messages.error(request, f"Import Failed: {report['errors'][0]}")
        else:
            messages.success(request, f"Students CSV processed: {report['added']} added, {report['updated']} updated, {report['skipped']} skipped.")
    else:
        messages.warning(request, "No file was selected for upload.")

    return redirect('csv_manager')


@login_required
def export_books_action(request):
    return CsvService.export_books()


@login_required
def export_students_action(request):
    return CsvService.export_students()


@login_required
def export_issued_action(request):
    return CsvService.export_issued_books()


@login_required
def export_returned_action(request):
    return CsvService.export_returned_books()


@login_required
def export_requests_action(request):
    return CsvService.export_requests()


@login_required
def download_sample_books(request):
    path = os.path.join(settings.BASE_DIR, 'sample_data', 'sample_books.csv')
    if os.path.exists(path):
        return FileResponse(open(path, 'rb'), as_attachment=True, filename='sample_books.csv')
    return HttpResponse("Sample file not found.", status=404)


@login_required
def download_sample_students(request):
    path = os.path.join(settings.BASE_DIR, 'sample_data', 'sample_students.csv')
    if os.path.exists(path):
        return FileResponse(open(path, 'rb'), as_attachment=True, filename='sample_students.csv')
    return HttpResponse("Sample file not found.", status=404)
