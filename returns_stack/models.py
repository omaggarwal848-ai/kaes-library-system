from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from transactions.models import BookReturn

class ReturnStackItem(models.Model):
    STATUS_CHOICES = (
        ('in_stack', 'In Return Stack (Awaiting Reshelving)'),
        ('shelved', 'Inspected & Reshelved (Popped)'),
    )

    book_return = models.ForeignKey(BookReturn, on_delete=models.CASCADE, null=True, blank=True, related_name='stack_items')
    book_title = models.CharField(max_length=255)
    book_isbn = models.CharField(max_length=50)
    student_name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=50)
    pushed_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stack')
    popped_at = models.DateTimeField(null=True, blank=True)
    popped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='popped_stack_items')
    condition = models.CharField(max_length=50, default='Good')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"StackItem #{self.id}: {self.book_title} (Status: {self.status})"

    def to_dict(self):
        return {
            'id': self.id,
            'book_title': self.book_title,
            'book_isbn': self.book_isbn,
            'student_name': self.student_name,
            'student_id': self.student_id,
            'pushed_at': self.pushed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'popped_at': self.popped_at.strftime('%Y-%m-%d %H:%M:%S') if self.popped_at else None,
            'popped_by': self.popped_by.username if self.popped_by else None,
            'condition': self.condition,
            'notes': self.notes,
        }
