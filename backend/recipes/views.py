from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.filters import RecipeFilter, CustomSearchFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (IngredientSerializer,
                                 RecipeCreateUpdateSerializer,
                                 RecipeListSerializer,
                                 RecipeMinifiedSerializer,
                                 RecipeShortLinkSerializer, TagSerializer)
from recipes.utils import generate_shopping_list
from users.pagination import CustomPageNumberPagination
from django.shortcuts import get_object_or_404, redirect


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('tags', 'ingredients').all()
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        return self._add_to(Favorite, request.user, recipe)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = self.get_object()
        return self._remove_from(Favorite, request.user, recipe)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(AllowAny,)
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        serializer = RecipeShortLinkSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self._add_to(ShoppingCart, request.user, recipe)
        return self._remove_from(ShoppingCart, request.user, recipe)

    def _add_to(self, model, user, recipe):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from(self, model, user, recipe):
        deleted, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепт не был добавлен ранее'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipeingredient__recipe__in_shopping_carts__user=request.user
        ).annotate(
            total_amount=Sum('recipeingredient__amount')
        ).values_list(
            'name',
            'total_amount',
            'measurement_unit'
        )
        return generate_shopping_list(ingredients)


def redirect_short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(recipe)
