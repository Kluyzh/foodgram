from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, SubscriptionViewSet, CustomTokenViewSet
from recipes.views import IngredientViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', CustomTokenViewSet.as_view({'post': 'login'}), name='token-login'),
    path('auth/token/logout/', CustomTokenViewSet.as_view({'post': 'logout'}), name='token-logout'),

    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({
        'post': 'create',
        'delete': 'destroy'
    }), name='subscribe'),

    path('', include(router.urls)),
]
