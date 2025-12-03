import django_filters.rest_framework as django_filters_rest
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Value
from django.db.models.functions import Concat


class UserSearchFilter(django_filters_rest.FilterSet):
    search = django_filters_rest.CharFilter(method='search_filter')

    class Meta:
        model = User
        fields = ['search']

    def search_filter(self, queryset, name, value):
        return queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(full_name__icontains=value)
        )



