from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    gender = models.CharField(max_length=50, blank=True)
    fans_count = models.IntegerField(default=0)
    works = models.CharField(max_length=500, blank=True)  # IDs dos livros correspondentes

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    ratings_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    text_reviews_count = models.IntegerField(default=0)
    work_ids = models.CharField(max_length=255)
    book_ids = models.CharField(max_length=255)
    works_count = models.IntegerField(default=1)
    authors = models.CharField(max_length=500, blank=True)  # IDs dos autores

    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relacionamento com o usuário
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Relacionamento com o livro
    added_at = models.DateTimeField(auto_now_add=True)  # Quando o livro foi adicionado

    class Meta:
        unique_together = ('user', 'book')  # Garantir que um usuário não possa adicionar o mesmo livro duas vezes