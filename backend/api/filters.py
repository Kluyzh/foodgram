import django_filters
from recipes.models import Recipe, Ingredient
from django.db.models import Q


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(method='filter_in_shopping_cart')
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = []

    def filter_is_favorited(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        if value:
            tags = value.split(',')
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        )
