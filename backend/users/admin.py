from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription

admin.site.register(FoodgramUser, UserAdmin)
admin.site.register(Subscription)
