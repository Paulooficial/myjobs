from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from books.views import BookViewSet, AuthorViewSet, FavoriteViewSet, RegisterView


# Router para books e authors
router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)

urlpatterns = [
    # Rota principal da API
    path('api/', include(router.urls)),

    # Endpoint para adicionar e listar favoritos
    path('api/favorites/list/', FavoriteViewSet.as_view({'get': 'list_favorites'}), name='favorite-list'),
    path('api/favorites/', FavoriteViewSet.as_view({'post': 'add_favorite'}), name='favorite-add'),

    # Endpoint para remover favoritos
    path('api/favorites/remove_favorite/', FavoriteViewSet.as_view({'post': 'remove_favorite'}), name='favorite-remove'),

    # Endpoint para recomendações
    path('api/favorites/recommendations/', FavoriteViewSet.as_view({'get': 'recommendations'}), name='favorite-recommendations'),

    # Endpoints de autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint para obter o token de acesso
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Endpoint para refresh do token

    # Endpoint de registro de novos usuários
    path('api/register/', RegisterView.as_view(), name='register'),
]



