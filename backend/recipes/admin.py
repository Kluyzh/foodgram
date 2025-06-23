from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Ingredient, Tag, Recipe

admin.site.unregister(Group)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)

    def favorite_count(self, obj):
        return obj.favorites.count()


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
