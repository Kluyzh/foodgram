from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer
from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
import base64
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "author", "ingredients",
            "is_favorited", "is_in_shopping_cart",
            "name", "image", "text", "cooking_time"
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return not user.is_anonymous and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return not user.is_anonymous and ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredients"
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True
    )
    tags_details = TagSerializer(source='tags', many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image",
            "name", "text", "cooking_time", "author", "tags_details", "id", "is_favorited", "is_in_shopping_cart"
        )

    def validate(self, data):
        # Валидация тегов
        # if not data.get('tags'):
        #     raise serializers.ValidationError("Необходимо указать теги")
        
        # # Валидация ингредиентов
        # ingredients = data.get('ingredients', [])
        # # if not ingredients:
        # #     raise serializers.ValidationError("Необходимо указать ингредиенты")
        
        # # Проверка дубликатов ингредиентов
        # ingredient_ids = [item['ingredient'] for item in ingredients]
        # if len(ingredient_ids) != len(set(ingredient_ids)):
        #     raise serializers.ValidationError(
        #         "Ингредиенты не должны повторяться"
        #     )

        # tags = data.get('tags', [])
        # # if not tags:
        # #     raise serializers.ValidationError("Необходимо указать ингредиенты")        

        # tags_ids = [item['ingredient'] for item in tags]
        # if len(tags_ids) != len(set(tags_ids)):
        #     raise serializers.ValidationError(
        #         "Ингредиенты не должны повторяться"
        #     )
        
        return data

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context["request"].user
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients", None)
        tags = validated_data.pop("tags", None)
        
        # Обновление основных полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновление тегов
        if tags is not None:
            instance.tags.set(tags)
        
        # Обновление ингредиентов
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients_data)
        
        return instance

    def to_representation(self, instance):
        """Переопределяем вывод: заменяем 'tags' на детали тегов."""
        representation = super().to_representation(instance)
        # Меняем 'tag_details' на 'tags' в ответе
        representation['tags'] = representation.pop('tags_details')
        return representation

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return not user.is_anonymous and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return not user.is_anonymous and ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()



class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data
