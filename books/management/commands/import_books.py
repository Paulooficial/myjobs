import csv
from django.core.management.base import BaseCommand
from books.models import Book, Author

class Command(BaseCommand):
    help = 'Import books from CSV'

    def handle(self, *args, **kwargs):
        with open('books.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Separar múltiplos autores e garantir que IDs sejam atribuídos
                    author_names = row['authors'].split('/')  # Autores separados por '/'
                    author_ids = []
                    
                    # Para cada autor, criar ou obter o autor e atualizar sua lista de obras
                    for name in author_names:
                        author, created = Author.objects.get_or_create(name=name.strip())
                        if created:
                            author.works = ''
                        author_ids.append(str(author.id))
                        if row['bookID'] not in author.works:
                            author.works += f"{row['bookID']},"
                        author.save()
                    
                    # Atualizar os campos de autores no livro
                    Book.objects.create(
                        title=row['title'],
                        ratings_count=int(row['ratings_count']) if row['ratings_count'].isdigit() else 0,
                        average_rating=float(row['average_rating']) if row['average_rating'].replace('.', '', 1).isdigit() else 0.0,
                        text_reviews_count=int(row.get('text_reviews_count', 0)),
                        work_ids=row.get('isbn', ''),
                        book_ids=row.get('isbn13', ''),
                        works_count=int(row.get('num_pages', 1)),
                        authors=",".join(author_ids)  # IDs dos autores
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro ao processar linha: {row}"))
                    self.stdout.write(self.style.ERROR(f"Erro: {e}"))
