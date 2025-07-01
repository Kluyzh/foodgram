from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import CustomSearchFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserCreateSerializer,
                             EmailAuthTokenSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeListSerializer, RecipeMinifiedSerializer,
                             RecipeShortLinkSerializer, SetAvatarSerializer,
                             TagSerializer, UserSerializer,
                             UserWithRecipesSerializer)
from api.utils import generate_shopping_list
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription

User = get_user_model()


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


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        author = self.get_object(author_id)
        if request.user == author:
            return Response(
                'Невозможно подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, author=author)
        serializer = UserWithRecipesSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )

        if not subscription.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)


class CustomTokenViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = EmailAuthTokenSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key})

    @action(
        detail=False, methods=['post'], permission_classes=(IsAuthenticated,)
    )
    def logout(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return UserSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['put'],
        detail=False,
        serializer_class=SetAvatarSerializer,
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        if request.data == {}:
            return Response(
                {'detail': 'Запрос не должен быть пустым'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            following__user=request.user
        )

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserWithRecipesSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        user = request.user
        if check_password(request.data['current_password'], user.password):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Текущий пароль неверный'},
                status=status.HTTP_400_BAD_REQUEST
            )
