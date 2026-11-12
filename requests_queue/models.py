from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import Student
from books.models import Book

class BookRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending In Queue'),
        ('approved', 'Approved / Ready for Pickup'),
        ('fulfilled', 'Fulfilled & Issued'),
        ('rejected', 'Rejected / Cancelled'),
    )

    request_id = models.CharField(max_length=30, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_requests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='hold_requests')
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    notification_sent = models.BooleanField(default=False)
    notification_message = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['request_date']

    def __str__(self):
        return f"{self.request_id} - {self.student.full_name} for '{self.book.title}' ({self.status})"

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'student_name': self.student.full_name,
            'student_id': self.student.student_id,
            'student_email': self.student.email,
            'book_title': self.book.title,
            'book_isbn': self.book.isbn,
            'book_available': self.book.available_copies,
            'request_date': self.request_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'notification_sent': self.notification_sent,
            'notification_message': self.notification_message,
            'remarks': self.remarks,
        }
