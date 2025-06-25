from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import Ingredient, Recipe, Tag, Favorite

admin.site.unregister(Group)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)

    readonly_fields = ('favorites_count',)

    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
