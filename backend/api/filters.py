from django_filters import rest_framework as filters_from_django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters_from_django_filters.FilterSet):
    is_favorited = filters_from_django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters_from_django_filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )
    tags = filters_from_django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=self.request.user)
        return queryset


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'name'
