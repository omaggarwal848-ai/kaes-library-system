from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from students.models import Student

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your username or email',
        'autocomplete': 'username',
        'required': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password',
        'required': True
    }))


class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a secure password (min 6 chars)'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'enrollment_year', 'address']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., STU2024009'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@campus.edu'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0199'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'enrollment_year': forms.NumberInput(attrs={'class': 'form-control', 'value': 2024}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hostel/Residence address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        username = cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "This username is already taken.")

        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "An account with this email already exists.")

        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar', 'bio', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
