from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from users.fields import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.following.filter(user=user).exists())


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label='Email',
        write_only=True
    )
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label='Token',
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                msg = 'Не удалось войти с указанными учетными данными.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Необходимо указать email и пароль.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
