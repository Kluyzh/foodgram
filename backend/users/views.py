from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token  # Импорт модели Token
from djoser.conf import settings
from .serializers import (
    UserSerializer,
    CustomUserCreateSerializer,
    SetAvatarSerializer,
    UserWithRecipesSerializer,
    EmailAuthTokenSerializer  # Импорт сериализатора
)
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from .models import Subscription
from .serializers import (
    UserSerializer,
    CustomUserCreateSerializer,
    SetAvatarSerializer,
    UserWithRecipesSerializer
)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import EmailAuthTokenSerializer
from django.contrib.auth.hashers import check_password

User = get_user_model()


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        author = self.get_object(author_id)
        if request.user == author:
            return Response('Невозможно подписаться на самого себя', status=status.HTTP_400_BAD_REQUEST)
        
        if Subscription.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Subscription.objects.create(user=request.user, author=author)
        serializer = UserWithRecipesSerializer(
            author, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        # author = self.get_object(author_id)
        author = get_object_or_404(User, id=author_id)
        # subscription = get_object_or_404(Subscription, user=request.user, author=author)
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
        # try:
        #     return User.objects.get(id=user_id)
        # except User.DoesNotExist:
        #     raise serializers.ValidationError(
        #         {'detail': 'Пользователь не dddddddddddddddddd'},
        #         code=status.HTTP_404_NOT_FOUND
        #     )



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

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        # Удаляем токен текущего пользователя
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return UserSerializer

    @action(
        ["get"], 
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['put'], 
        detail=False,
        # permission_classes=[permissions.IsAuthenticated],
        serializer_class=SetAvatarSerializer,
        # url_path='me/avatar',
    )
    def avatar(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Требуется авторизация"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if request.data == {}:
            return Response({'detail': 'Запрос не должен быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Требуется авторизация"},
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
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            following__user=request.user
        )
        
        # Пагинация
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
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, request):
        user = request.user
        if check_password(request.data['current_password'], user.password):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Текущий пароль неверный"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
