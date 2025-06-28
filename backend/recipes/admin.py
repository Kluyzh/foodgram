from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import Favorite, Ingredient, Recipe, Tag, ShoppingCart, RecipeIngredient

admin.site.unregister(Group)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'display_tags')
    search_fields = ('name', 'author__username', 'author__email', 'tags')
    list_filter = ('tags', 'author')

    readonly_fields = ('favorites_count',)

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description='Теги')
    def display_tags(self, obj):
        return ','.join([tag.name for tag in obj.tags.all()])


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredient)
