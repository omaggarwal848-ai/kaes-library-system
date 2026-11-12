from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-book', help_text="FontAwesome icon class, e.g., fa-laptop-code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()


class Book(models.Model):
    isbn = models.CharField(max_length=30, unique=True, help_text="ISBN or unique Book Accession Number")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.CharField(max_length=150, blank=True)
    publication_year = models.PositiveIntegerField(default=2023)
    edition = models.CharField(max_length=50, blank=True, default='1st Edition')
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True, help_text="Rack/Shelf location e.g., Shelf A-12")
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author} ({self.isbn})"

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def issued_copies(self):
        return max(0, self.total_copies - self.available_copies)
