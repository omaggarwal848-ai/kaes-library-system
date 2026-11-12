from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
    )

    DEPARTMENT_CHOICES = (
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Data Science & AI', 'Data Science & AI'),
        ('Business Administration', 'Business Administration'),
        ('General Sciences', 'General Sciences'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_record')
    student_id = models.CharField(max_length=30, unique=True, help_text="Unique Student Roll/Registration ID")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='Computer Science & Engineering')
    enrollment_year = models.PositiveIntegerField(default=2024)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def currently_issued_count(self):
        return self.issues.filter(status='issued').count()

    @property
    def overdue_count(self):
        today = timezone.now().date()
        return self.issues.filter(status='issued', due_date__lt=today).count()

    @property
    def total_fines(self):
        total = sum(issue.calculate_fine() for issue in self.issues.filter(status='issued'))
        paid = sum(issue.fine_amount for issue in self.issues.filter(fine_paid=True))
        return total
