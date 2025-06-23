from rest_framework import viewsets, permissions
from .models import Tag
from .serializers import TagSerializer
from rest_framework.exceptions import PermissionDenied 
from api.permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # По спецификации пагинация не требуется


from rest_framework import viewsets, permissions, filters
from .models import Ingredient
from .serializers import IngredientSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # По спецификации пагинация не требуется
    
    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']  # Поиск по началу названия


from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Recipe, Favorite, ShoppingCart
from .serializers import (
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    RecipeShortLinkSerializer
)
from .filters import RecipeFilter

class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter  # Кастомный фильтр

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'tags',
            'ingredient_amounts__ingredient',
            'author'
        ).select_related('author').distinct()
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'favorite', 'shopping_cart']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Проверка авторства в perform_*
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не автор этого рецепта")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        serializer = RecipeShortLinkSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if not favorite.exists():
                return Response(
                    {'detail': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if not cart_item.exists():
                return Response(
                    {'detail': 'Рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=False, 
        methods=['get'], 
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        # Формируем текстовый файл со списком покупок
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        
        # Собираем ингредиенты
        ingredients = {}
        for item in shopping_cart:
            for ingredient in item.recipe.ingredients.all():
                amount = ingredient.amount
                key = (ingredient.name, ingredient.measurement_unit)
                ingredients[key] = ingredients.get(key, 0) + amount
        
        # Формируем содержимое файла
        content = "Список покупок:\n\n"
        for (name, unit), amount in ingredients.items():
            content += f"- {name}: {amount} {unit}\n"
        
        # Возвращаем файл
        from django.http import HttpResponse
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response