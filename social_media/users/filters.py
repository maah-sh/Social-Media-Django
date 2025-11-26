import django_filters.rest_framework as django_filters_rest
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.db.models import Q, Value, F
from django.db.models.functions import Concat


class UserSearchFilter(django_filters_rest.FilterSet):
    username__iexact = django_filters_rest.CharFilter(field_name='username', lookup_expr='iexact')
    search = django_filters_rest.CharFilter(method='search_filter')
    search_full_text = django_filters_rest.CharFilter(method='full_text_search')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters_rest.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }

    def search_filter(self, queryset, name, value):
        return queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(full_name__icontains=value)
        )

    def full_text_search(self, queryset, name, value):
        return queryset.alias(
            vector=SearchVector('username', 'first_name', 'last_name'),
            query=SearchQuery(value)
        ).filter(vector=F('query')).annotate(rank=SearchRank(F('vector'), F('query'))).order_by('-rank')



