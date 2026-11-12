from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime
from books.models import Book
from students.models import Student

class BookIssue(models.Model):
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )

    issue_id = models.CharField(max_length=30, unique=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='issues')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_transactions')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.issue_id} - {self.book.title} to {self.student.full_name}"

    def calculate_fine(self, rate_per_day=Decimal('2.00')):
        """Calculates late fine if overdue: $2.00 / day overdue"""
        if self.status == 'returned' and self.return_date:
            ref_date = self.return_date
        else:
            ref_date = timezone.now().date()
        
        if ref_date > self.due_date:
            days_overdue = (ref_date - self.due_date).days
            return Decimal(days_overdue) * rate_per_day
        return Decimal('0.00')

    @property
    def is_overdue(self):
        if self.status == 'issued':
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_remaining_or_overdue(self):
        today = timezone.now().date()
        diff = (self.due_date - today).days
        return diff


class BookReturn(models.Model):
    issue = models.OneToOneField(BookIssue, on_delete=models.CASCADE, related_name='return_detail')
    return_date = models.DateTimeField(default=timezone.now)
    returned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_returns')
    book_condition = models.CharField(max_length=50, default='Good', choices=[
        ('Good', 'Good / Normal'),
        ('Fair', 'Fair / Minor Wear'),
        ('Damaged', 'Damaged / Binding Wear'),
        ('Lost', 'Lost'),
    ])
    fine_collected = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-return_date']

    def __str__(self):
        return f"Return for {self.issue.issue_id} on {self.return_date.strftime('%Y-%m-%d %H:%M')}"


class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('BOOK_ADDED', 'Book Added'),
        ('BOOK_UPDATED', 'Book Updated'),
        ('BOOK_DELETED', 'Book Deleted'),
        ('BOOK_ISSUED', 'Book Issued'),
        ('BOOK_RETURNED', 'Book Returned'),
        ('STACK_PUSH', 'Stack Push'),
        ('STACK_POP', 'Stack Pop'),
        ('STACK_PEEK', 'Stack Peek'),
        ('QUEUE_ENQUEUE', 'Queue Enqueue'),
        ('QUEUE_DEQUEUE', 'Queue Dequeue'),
        ('QUEUE_PEEK', 'Queue Peek'),
        ('CSV_IMPORT', 'CSV Import'),
        ('CSV_EXPORT', 'CSV Export'),
        ('STUDENT_ADDED', 'Student Added'),
        ('USER_LOGIN', 'User Login'),
        ('USER_LOGOUT', 'User Logout'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_str}: {self.action_type}"
