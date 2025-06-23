from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Subscription
from .serializers import (
    UserSerializer, 
    UserCreateSerializer,
    SetPasswordSerializer,
    SetAvatarSerializer,
    
)
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.serializers import UserWithRecipesSerializer

User = get_user_model()

class UserViewSet(DjoserUserViewSet):
    serializer_classes = {
        'create': UserCreateSerializer,
        'current_user': UserSerializer,
        'set_password': SetPasswordSerializer,
        'set_avatar': SetAvatarSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, UserSerializer)

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = lambda: request.user
        return super().me(request, *args, **kwargs)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        current_password = serializer.data.get("current_password")
        new_password = serializer.data.get("new_password")
        
        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["put"], detail=False, url_path="me/avatar")
    def set_avatar(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(["delete"], detail=False, url_path="me/avatar")
    def delete_avatar(self, request, *args, **kwargs):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        
        # Пагинация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(["post", "delete"], detail=True)
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        
        if request.method == "POST":
            if user == author:
                return Response(
                    {"detail": "Cannot subscribe to yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"detail": "Already subscribed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Subscription.objects.create(user=user, author=author)
            serializer = UserWithRecipesSerializer(
                author, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == "DELETE":
            subscription = Subscription.objects.filter(user=user, author=author)
            if not subscription.exists():
                return Response(
                    {"detail": "Subscription not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'], url_path='me/avatar')
    def set_avatar(self, request):
        user = request.user
        serializer = SetAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='me/avatar')
    def delete_avatar(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import TokenCreateSerializer, TokenResponseSerializer

class TokenCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = TokenCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response(
            TokenResponseSerializer(token).data,
            status=status.HTTP_200_OK
        )

class TokenDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserCreateSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )