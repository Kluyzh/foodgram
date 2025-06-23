from rest_framework.routers import DefaultRouter
from django.urls import path, include
from users.views import UserViewSet, TokenCreateView, TokenDestroyView
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
# urls.py
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('api/auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('api/users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('api/users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-detail'),
]