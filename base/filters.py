import django_filters
from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class ArchiveFilter(django_filters.FilterSet):
    is_active = django_filters.ChoiceFilter(
        method='filter_is_active',
        choices=(("true", "true"), ("false", "false"), ("any", "any"))
    )

    class Meta:
        abstract = True

    @extend_schema_field(serializers.ChoiceField(choices=["true", "false", "any"]))
    def filter_is_active(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(is_active=True)
        elif value == 'false':
            return queryset.filter(is_active=False)
        else:
            return queryset.filter(Q(is_active=False) | Q(is_active=True))