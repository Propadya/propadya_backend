from collections import defaultdict
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from base.swagger import set_query_params
from rest_framework.generics import ListAPIView
from base.views import CustomViewSet
from event.filters import EventFilterSet
from event.models import EventModel
from event.serializer import EventSerializer, EventDetailsSerializer


@extend_schema(tags=['Public Event'])
class CommonEventViewSet(CustomViewSet):
    http_method_names = ["get", ]
    permission_classes = (AllowAny,)
    periodic_delete_enabled = True
    cache_prefix = []
    cache_key = ""
    model_class = EventModel
    filterset_class = EventFilterSet
    search_fields = ["id", "title", "status", "district", "city", "country", "event_type"]
    serializer_class = EventSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventDetailsSerializer
        return EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


@extend_schema(
    tags=['Regional Data'],
    parameters=set_query_params(
        'list',
        [
            {'name': 'is_active', "enum": ["true", "false", "any"], 'description': 'Should filter by active items'},
            {'name': 'approval_status', 'description': 'The property status'}
        ]
    )
)
class EventRegionalDataApiView(ListAPIView):
    permission_classes = (AllowAny,)
    cache_prefix = []
    cache_key = ""
    model_class = EventModel
    filterset_class = EventFilterSet
    search_fields = ["id", "title", "status", "district", "city", "country", "location", "event_type"]
    serializer_class = EventSerializer

    def get_queryset(self):
        types = ["true", "false", "any"]
        obj_type = self.request.query_params.get("is_active", "true").lower()
        if not obj_type in types:
            raise ValueError(f"Invalid type '{obj_type}'")
        if obj_type == "true":
            qs = self.model_class.active_objects
        elif obj_type == "false":
            qs = self.model_class.inactive_objects
        else:
            qs = self.model_class.objects
        event_status = self.request.query_params.get("status")
        if event_status:
            qs = qs.filter(status=event_status)
        else:
            qs = qs.all()
        return qs.order_by("-created_at").values("country", "district", "city").distinct()

    def list(self, request, *args, **kwargs):
        data = []
        qs = self.get_queryset()
        tree = defaultdict(lambda: defaultdict(set))

        for row in qs:
            country = row["country"]
            district = row["district"]
            city = row["city"]
            if country and district and city:
                tree[country][district].add(city)

        for country, districts in tree.items():
            district_data = []
            for district, cities in districts.items():
                district_data.append({
                    "name": district,
                    "cities": [{"name": city} for city in sorted(cities)]
                })

            data.append({
                "country_name": country,
                "district": district_data
            })

        return Response(data, status=status.HTTP_200_OK)
