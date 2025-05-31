import django_filters
from base.filters import ArchiveFilter
from event.models import EventModel

class EventFilterSet(ArchiveFilter):
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')


    start_date = django_filters.DateFilter(field_name="start_date",lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="end_date", lookup_expr='lte')
    start_time = django_filters.TimeFilter(field_name="start_time", lookup_expr='gte')
    end_time = django_filters.TimeFilter(field_name="end_time", lookup_expr='lte')
    category = django_filters.CharFilter(method='filter_category')
    sub_category = django_filters.CharFilter(method='filter_sub_category')

    class Meta:
        model = EventModel
        exclude = [
            "event_image",
            "is_active",
            "meeting_link",
            "text_color",
            "bg_color",
            "location_link",
            "admin_comment",
            "registration_link",
            "event_video",
        ]

    def filter_category(self, queryset, name, value):
        categories = value.split(",")
        return queryset.filter(category__overlap=categories)

    def filter_sub_category(self, queryset, name, value):
        sub_categories = value.split(",")
        return queryset.filter(sub_category__overlap=sub_categories)




