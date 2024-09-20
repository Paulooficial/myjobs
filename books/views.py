from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q  # Importar Q para consultas complexas
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, Favorite
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated  # Importar permissão
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    # Permitir a busca por título ou autor
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |  # Busca por título
                Q(authors__in=Author.objects.filter(name__icontains=search_query))  # Busca por nome de autor
            )
        
        return queryset

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

    # Permitir a busca por nome de autor
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)  # Busca por nome de autor
            )
        
        return queryset

class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Exigir que o usuário esteja autenticado

    @action(detail=False, methods=['post'])
    def add_favorite(self, request):
        book_id = request.data.get('book_id')
        user = request.user  # Garantir que o usuário esteja autenticado

        # Limitar a lista de favoritos a 20
        if Favorite.objects.filter(user=user).count() >= 20:
            return Response({"error": "Limite de 20 livros favoritos alcançado."}, status=status.HTTP_400_BAD_REQUEST)

        book = Book.objects.get(id=book_id)
        favorite, created = Favorite.objects.get_or_create(user=user, book=book)

        if not created:
            return Response({"message": "Livro já está na lista de favoritos."}, status=status.HTTP_200_OK)

        return Response({"message": "Livro adicionado aos favoritos."}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def remove_favorite(self, request):
        book_id = request.data.get('book_id')
        user = request.user  # Garantir que o usuário esteja autenticado

        book = Book.objects.get(id=book_id)
        Favorite.objects.filter(user=user, book=book).delete()

        return Response({"message": "Livro removido dos favoritos."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        user = request.user  # Garantir que o usuário esteja autenticado
        favorites = Favorite.objects.filter(user=user).values_list('book_id', flat=True)

        if not favorites:
            return Response({"message": "Nenhum livro favorito encontrado."}, status=status.HTTP_200_OK)

        # Simples lógica para recomendar livros semelhantes
        recommendations = Book.objects.exclude(id__in=favorites)[:5]

        if not recommendations:
            return Response({"message": "Nenhuma recomendação disponível."}, status=status.HTTP_200_OK)

        recommended_books = [{"id": book.id, "title": book.title} for book in recommendations]

        return Response({"recommendations": recommended_books}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])  # Nova ação para listar favoritos
    def list_favorites(self, request):
        user = request.user  # Garantir que o usuário esteja autenticado
        favorites = Favorite.objects.filter(user=user)

        if not favorites:
            return Response({"message": "Nenhum favorito encontrado."}, status=status.HTTP_200_OK)

        favorite_books = [{"id": fav.book.id, "title": fav.book.title} for fav in favorites]
        
        return Response({"results": favorite_books}, status=status.HTTP_200_OK)

    

# Serializer para registro
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# View para registrar usuários
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # Permitir que usuários não autenticados acessem o registro
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Gerar tokens JWT para o novo usuário
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)