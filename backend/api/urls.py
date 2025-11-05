from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomTokenViewSet, CustomUserViewSet,
                    IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet, redirect_short_link)

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', CustomTokenViewSet.as_view(
        {'post': 'login'}
    ), name='token-login'),

    path('auth/token/logout/', CustomTokenViewSet.as_view(
        {'post': 'logout'}
    ), name='token-logout'),

    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view(
        {
            'post': 'create',
            'delete': 'destroy'
        }
    ), name='subscribe'),
    path('<int:pk>/', redirect_short_link, name='short_recipe_link'),

    path('', include(router.urls)),
]
