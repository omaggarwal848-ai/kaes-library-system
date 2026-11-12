from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import BookIssue, BookReturn
from books.models import Book
from students.models import Student

class BookIssueForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(status='active'),
        widget=forms.Select(attrs={'class': 'form-select select2-enable', 'required': True})
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_copies__gt=0),
        widget=forms.Select(attrs={'class': 'form-select select2-enable', 'required': True})
    )

    class Meta:
        model = BookIssue
        fields = ['student', 'book', 'issue_date', 'due_date', 'notes']
        widgets = {
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional issue remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['issue_date'].initial = today
        self.fields['due_date'].initial = today + timedelta(days=14)

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        student = cleaned_data.get('student')
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')

        if book and book.available_copies <= 0:
            self.add_error('book', f"'{book.title}' has 0 available copies currently in library.")

        if student:
            # Check maximum loan limit (e.g., 5 books)
            active_count = student.currently_issued_count
            if active_count >= 5:
                self.add_error('student', f"{student.full_name} already has {active_count} issued books (limit 5).")

        if issue_date and due_date and due_date <= issue_date:
            self.add_error('due_date', "Due date must be after the issue date.")

        return cleaned_data


class BookReturnForm(forms.ModelForm):
    class Meta:
        model = BookReturn
        fields = ['book_condition', 'fine_collected', 'remarks']
        widgets = {
            'book_condition': forms.Select(attrs={'class': 'form-select'}),
            'fine_collected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'min': 0}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Return inspection notes'}),
        }
