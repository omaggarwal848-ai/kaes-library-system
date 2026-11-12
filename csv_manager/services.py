import io
import pandas as pd
from django.utils import timezone
from django.http import HttpResponse
from books.models import Book, Category
from students.models import Student
from transactions.models import BookIssue, BookReturn, ActivityLog
from requests_queue.models import BookRequest

class CsvService:
    @staticmethod
    def import_books(csv_file, user=None):
        report = {
            'total_rows': 0,
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        try:
            # Read CSV with pandas
            df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
            report['total_rows'] = len(df)

            required_cols = {'title', 'author', 'isbn'}
            if not required_cols.issubset(set(df.columns)):
                missing = required_cols - set(df.columns)
                report['errors'].append(f"Missing mandatory CSV columns: {', '.join(missing)}")
                return report

            for idx, row in df.iterrows():
                row_num = idx + 2
                title = str(row.get('title', '')).strip()
                author = str(row.get('author', '')).strip()
                isbn = str(row.get('isbn', '')).strip()
                category_name = str(row.get('category', 'General')).strip()
                publisher = str(row.get('publisher', '')).strip()
                edition = str(row.get('edition', '1st Edition')).strip()
                shelf = str(row.get('shelf_location', 'Section General')).strip()
                desc = str(row.get('description', '')).strip()

                if not title or not author or not isbn:
                    report['skipped'] += 1
                    report['errors'].append(f"Row {row_num}: Skipped because title, author, or ISBN is empty.")
                    continue

                try:
                    pub_year = int(row.get('publication_year', 2023))
                except (ValueError, TypeError):
                    pub_year = 2023

                try:
                    total_copies = int(row.get('total_copies', 1))
                    if total_copies < 1:
                        total_copies = 1
                except (ValueError, TypeError):
                    total_copies = 1

                # Category handling
                cat_obj, _ = Category.objects.get_or_create(
                    name=category_name if category_name else 'General',
                    defaults={'description': f'Category for {category_name}'}
                )

                # Check if ISBN already exists
                existing_book = Book.objects.filter(isbn=isbn).first()
                if existing_book:
                    existing_book.title = title
                    existing_book.author = author
                    existing_book.category = cat_obj
                    existing_book.publisher = publisher
                    existing_book.publication_year = pub_year
                    existing_book.edition = edition
                    existing_book.shelf_location = shelf
                    existing_book.description = desc
                    # Increase total and available copies proportionally
                    diff = total_copies - existing_book.total_copies
                    existing_book.total_copies = total_copies
                    existing_book.available_copies = max(0, existing_book.available_copies + diff)
                    existing_book.save()
                    report['updated'] += 1
                else:
                    Book.objects.create(
                        title=title,
                        author=author,
                        isbn=isbn,
                        category=cat_obj,
                        publisher=publisher,
                        publication_year=pub_year,
                        edition=edition,
                        total_copies=total_copies,
                        available_copies=total_copies,
                        shelf_location=shelf,
                        description=desc
                    )
                    report['added'] += 1

            ActivityLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action_type='CSV_IMPORT',
                description=f"Imported Books CSV: {report['added']} added, {report['updated']} updated, {report['skipped']} skipped."
            )

        except Exception as e:
            report['errors'].append(f"Fatal error reading CSV file: {str(e)}")

        return report

    @staticmethod
    def import_students(csv_file, user=None):
        report = {
            'total_rows': 0,
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        try:
            df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
            report['total_rows'] = len(df)

            required_cols = {'student_id', 'first_name', 'last_name', 'email'}
            if not required_cols.issubset(set(df.columns)):
                missing = required_cols - set(df.columns)
                report['errors'].append(f"Missing mandatory CSV columns: {', '.join(missing)}")
                return report

            for idx, row in df.iterrows():
                row_num = idx + 2
                student_id = str(row.get('student_id', '')).strip().upper()
                first_name = str(row.get('first_name', '')).strip()
                last_name = str(row.get('last_name', '')).strip()
                email = str(row.get('email', '')).strip().lower()
                phone = str(row.get('phone', '')).strip()
                department = str(row.get('department', 'Computer Science & Engineering')).strip()
                address = str(row.get('address', '')).strip()
                status = str(row.get('status', 'active')).strip().lower()
                if status not in ['active', 'suspended', 'graduated']:
                    status = 'active'

                if not student_id or not first_name or not email:
                    report['skipped'] += 1
                    report['errors'].append(f"Row {row_num}: Missing student_id, first_name, or email.")
                    continue

                try:
                    enrollment_year = int(row.get('enrollment_year', 2024))
                except (ValueError, TypeError):
                    enrollment_year = 2024

                # Check if exists by student_id or email
                student = Student.objects.filter(student_id=student_id).first()
                if not student:
                    student = Student.objects.filter(email=email).first()

                if student:
                    student.first_name = first_name
                    student.last_name = last_name
                    student.phone = phone
                    student.department = department
                    student.enrollment_year = enrollment_year
                    student.address = address
                    student.status = status
                    student.save()
                    report['updated'] += 1
                else:
                    Student.objects.create(
                        student_id=student_id,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        department=department,
                        enrollment_year=enrollment_year,
                        address=address,
                        status=status
                    )
                    report['added'] += 1

            ActivityLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action_type='CSV_IMPORT',
                description=f"Imported Students CSV: {report['added']} added, {report['updated']} updated, {report['skipped']} skipped."
            )

        except Exception as e:
            report['errors'].append(f"Fatal error reading CSV file: {str(e)}")

        return report

    @staticmethod
    def export_books():
        books = Book.objects.all().select_related('category')
        data = []
        for b in books:
            data.append({
                'ISBN': b.isbn,
                'Title': b.title,
                'Author': b.author,
                'Category': b.category.name if b.category else 'General',
                'Publisher': b.publisher,
                'Publication Year': b.publication_year,
                'Edition': b.edition,
                'Total Copies': b.total_copies,
                'Available Copies': b.available_copies,
                'Issued Copies': b.issued_copies,
                'Shelf Location': b.shelf_location,
                'Added Date': b.created_at.strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kaes_books_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @staticmethod
    def export_students():
        students = Student.objects.all()
        data = []
        for s in students:
            data.append({
                'Student ID': s.student_id,
                'First Name': s.first_name,
                'Last Name': s.last_name,
                'Email': s.email,
                'Phone': s.phone,
                'Department': s.department,
                'Enrollment Year': s.enrollment_year,
                'Status': s.status,
                'Currently Issued Books': s.currently_issued_count,
                'Overdue Books': s.overdue_count,
                'Joined Date': s.created_at.strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kaes_students_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @staticmethod
    def export_issued_books():
        issues = BookIssue.objects.all().select_related('book', 'student')
        data = []
        for issue in issues:
            data.append({
                'Issue ID': issue.issue_id,
                'Book Title': issue.book.title,
                'ISBN': issue.book.isbn,
                'Student ID': issue.student.student_id,
                'Student Name': issue.student.full_name,
                'Issue Date': issue.issue_date.strftime('%Y-%m-%d'),
                'Due Date': issue.due_date.strftime('%Y-%m-%d'),
                'Return Date': issue.return_date.strftime('%Y-%m-%d') if issue.return_date else 'Not Returned',
                'Status': issue.status,
                'Calculated Fine ($)': f"{issue.calculate_fine():.2f}",
                'Fine Paid': 'Yes' if issue.fine_paid else 'No'
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kaes_issued_books_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @staticmethod
    def export_returned_books():
        returns = BookReturn.objects.all().select_related('issue__book', 'issue__student', 'returned_to')
        data = []
        for ret in returns:
            data.append({
                'Issue ID': ret.issue.issue_id,
                'Book Title': ret.issue.book.title,
                'Student Name': ret.issue.student.full_name,
                'Return Date': ret.return_date.strftime('%Y-%m-%d %H:%M'),
                'Condition': ret.book_condition,
                'Fine Collected ($)': f"{ret.fine_collected:.2f}",
                'Processed By': ret.returned_to.username if ret.returned_to else 'System',
                'Remarks': ret.remarks
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kaes_returned_books_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @staticmethod
    def export_requests():
        requests = BookRequest.objects.all().select_related('book', 'student')
        data = []
        for req in requests:
            data.append({
                'Request ID': req.request_id,
                'Book Title': req.book.title,
                'ISBN': req.book.isbn,
                'Student ID': req.student.student_id,
                'Student Name': req.student.full_name,
                'Request Date': req.request_date.strftime('%Y-%m-%d %H:%M'),
                'Status': req.status,
                'Notification Sent': 'Yes' if req.notification_sent else 'No',
                'Remarks': req.remarks
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kaes_pending_requests_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
