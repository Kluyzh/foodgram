from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64
import uuid
from users.models import Subscription

User = get_user_model()

# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             filename = f"{uuid.uuid4()}.{ext}"
#             data = ContentFile(base64.b64decode(imgstr), name=filename)
#         return super().to_internal_value(data)

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 
            'first_name', 'last_name', 
            'is_subscribed', 'avatar'
        )
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 
            'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

class SetAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)





from rest_framework.authtoken.models import Token

class TokenCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class TokenResponseSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')
    
    class Meta:
        model = Token
        fields = ('auth_token',)

