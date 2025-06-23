from django_filters import rest_framework as filters
from .models import Recipe

class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_in_shopping_cart')
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Tags'
    )
    
    class Meta:
        model = Recipe
        fields = []
    
    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset
    
    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_carts__user=user)
        return queryset
    
    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        
        # Поддерживаем несколько тегов через запятую
        tags = value.split(',') if isinstance(value, str) else value
        return queryset.filter(tags__slug__in=tags).distinct()