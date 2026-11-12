from django import forms
from .models import Book, Category

class BookForm(forms.ModelForm):
    new_category_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or type new category name to add'})
    )

    class Meta:
        model = Book
        fields = [
            'isbn', 'title', 'author', 'category', 'publisher',
            'publication_year', 'edition', 'total_copies', 'available_copies',
            'shelf_location', 'description', 'cover_image'
        ]
        widgets = {
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 978-0132350884'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author(s) Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publisher Name'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1800, 'max': 2100}),
            'edition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2nd Edition'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rack CS-04'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Book summary or notes'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        available = cleaned_data.get('available_copies')
        if total is not None and available is not None and available > total:
            self.add_error('available_copies', "Available copies cannot exceed total copies.")

        new_cat = cleaned_data.get('new_category_name')
        if new_cat:
            cat_obj, _ = Category.objects.get_or_create(name=new_cat.strip())
            cleaned_data['category'] = cat_obj
            self.cleaned_data['category'] = cat_obj

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-laptop-code'}),
        }
