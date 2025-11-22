import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import SpecialistProfile, Category

User = get_user_model()

class SpecialistFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="specialist_profile__hourly_rate", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="specialist_profile__hourly_rate", lookup_expr='lte')
    rating = django_filters.NumberFilter(method='filter_rating')
    category = django_filters.ModelMultipleChoiceFilter(
        field_name="specialist_profile__categories",
        queryset=Category.objects.all(),
        to_field_name="slug",
    )
    
    class Meta:
        model = User
        fields = ['min_price', 'max_price', 'rating', 'category']

    def filter_rating(self, queryset, name, value):
        if value:
            return queryset.filter(rating__gte=value)
        return queryset
