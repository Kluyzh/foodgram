from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, SubscriptionViewSet, CustomTokenViewSet
from recipes.views import IngredientViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

# urlpatterns = [
#     path('v1/', include(api_v1_router.urls)),
#     path('auth/', include('djoser.urls.authtoken')),
#     path('auth/', include('djoser.urls')),
# ]

router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    # Эндпоинты для токенов
    path('auth/token/login/', CustomTokenViewSet.as_view({'post': 'login'}), name='token-login'),
    path('auth/token/logout/', CustomTokenViewSet.as_view({'post': 'logout'}), name='token-logout'),
    
    # Эндпоинты подписок
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({
        'post': 'create', 
        'delete': 'destroy'
    }), name='subscribe'),
    
    # Другие эндпоинты
    path('users/subscriptions/', CustomUserViewSet.as_view({'get': 'subscriptions'}), name='subscriptions'),
    path('users/me/avatar/', CustomUserViewSet.as_view({
        'put': 'avatar', 
        'delete': 'delete_avatar'
    }), name='avatar'),
    
    # Подключение роутера
    path('', include(router.urls)),
]
