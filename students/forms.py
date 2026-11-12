from django import forms
from .models import Student
import random

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'enrollment_year', 'status', 'address']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STU2024010'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@campus.edu'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0199'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'enrollment_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2030}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hostel/Residence Address'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('student_id'):
            # Auto-generate suggestion
            rand_id = f"STU2024{random.randint(100, 999)}"
            self.fields['student_id'].initial = rand_id
