from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_subscribers_count', 'get_recipes_count')
    search_fields = ('username', 'email')
    readonly_fields = ('get_subscribers_count', 'get_recipes_count')

    @admin.display(description='Кол-во подписчиков')
    def get_subscribers_count(self, obj):
        return obj.following.count()

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes.count()


admin.site.register(Subscription)
