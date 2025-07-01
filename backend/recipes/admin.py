from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

admin.site.unregister(Group)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name', 'author', 'display_cooking_time', 'display_tags',
        'favorites_count', 'display_ingredients', 'image_preview'
    )
    search_fields = ('name', 'author__username', 'author__email', 'tags__name')
    list_filter = ('tags', 'author')
    readonly_fields = ('favorites_count',)

    @admin.display(description='Время приготовления (мин)')
    def display_cooking_time(self, obj):
        return obj.cooking_time

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, obj):
        return '<br>'.join(
            f'<span class="italic">{tag.name}</span>' for tag in obj.tags.all()
        )

    @admin.display(description='Ингредиенты')
    @mark_safe
    def display_ingredients(self, obj):
        return '<br>'.join(
            f'<span class="italic">{ingredient.name}</span>'
            for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px;">'
        return 'Нет изображения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredient)
