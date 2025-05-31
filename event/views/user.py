from datetime import timedelta, date as dt
from functools import reduce
from operator import or_

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, OuterRef, Subquery
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiExample
from nested_multipart_parser import NestedParser
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from base.enum import EventType, EventStatus, EventSubCategoryEnum, UserRoleEnum, EventCategoryEnum
from base.swagger import set_query_params
from base.views import CustomViewSet
from event.filters import EventFilterSet
from event.models import EventModel, EventContactPerson
from event.serializer import EventSerializer, EventCreateSerializer, EventDetailsSerializer, \
    EventContactPersonSerializer
from rest_framework.permissions import AllowAny


# Create your views here.


@extend_schema(tags=['Event'])
class EventViewSet(CustomViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = (AllowAny, )
    periodic_delete_enabled = True
    cache_prefix = []
    cache_key = ""
    model_class = EventModel
    filterset_class = EventFilterSet
    search_fields = ["id", "title", "status", "district", "city", "country", "event_type"]
    serializer_class = EventSerializer
    # parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update", "create"]:
            return EventCreateSerializer
        elif self.action == "retrieve":
            return EventDetailsSerializer
        return EventSerializer

    def validate_data(self, requested_data):
        """
        Custom validation for event creation and updates.
        """
        parser = NestedParser(requested_data)

        # Validate incoming nested data
        if not parser.is_valid():
            raise ValidationError(parser.errors)

        # Extract and prepare main data for the update
        data = parser.validate_data
        start_date = data.get("start_date", None) or None
        end_date = data.get("end_date", None) or None
        start_time = data.get("start_time", None) or None
        end_time = data.get("end_time", None) or None
        is_all_day = data.get("is_all_day", False) or False
        event_image = data.get("event_image")

        # Ensure start_date and end_date are not None
        if not start_date or not end_date:
            raise serializers.ValidationError("Both start_date and end_date are required.")

        # Ensure start_date is before end_date
        if start_date > end_date:
            raise serializers.ValidationError("The start date cannot be after the end date.")

        # If it's not an all-day event, validate start_time and end_time
        if not is_all_day:
            if not start_time or not end_time:
                raise serializers.ValidationError("Start time and end time are required for non-all-day events.")

            if start_date == end_date and start_time >= end_time:
                raise serializers.ValidationError("Start time must be before end time on the same day.")

        # Ensure valid link or location based on event type
        if data.get("event_type") == EventType.ONLINE.value:
            meeting_link = data.get("meeting_link")
            data["location"] = None
            data["location_link"] = None
            data["country"] = None
            data["district"] = None
            data["city"] = None
            if not meeting_link:
                raise serializers.ValidationError("Meeting link is required for online meeting.")
        elif data.get("event_type") == EventType.OFFLINE.value:
            location = data.get("location")
            country = data.get("country")
            district = data.get("district")
            city = data.get("city")
            if not location:
                raise serializers.ValidationError("Location is required for offline meeting.")
            if not country:
                raise serializers.ValidationError("Country is required for offline meeting.")
            if not district:
                raise serializers.ValidationError("District is required for offline meeting.")
            if not city:
                raise serializers.ValidationError("City is required for offline meeting.")
        # Remove event_image from data if it's a string (invalid file type)
        if isinstance(event_image, str) or event_image in ['null', 'None', 'undefined']:
            data.pop("event_image")

        category_str = data.get("category", "")
        sub_category_str = data.get("sub_category", "")

        # Convert comma-separated strings to lists
        category = category_str.split(",") if isinstance(category_str, str) else category_str
        sub_category = sub_category_str.split(",") if isinstance(sub_category_str, str) else sub_category_str

        # Ensure lists are properly formatted (no extra nesting)
        category = [c.strip() for c in category] if isinstance(category, list) else []
        sub_category = [sc.strip() for sc in sub_category] if isinstance(sub_category, list) else []

        # Assign cleaned values back to data
        data["category"] = category
        data["sub_category"] = sub_category
        registration_available = data.get("registration_available", False)
        if registration_available:
            registration_last_date = data.get("registration_last_date")
            if registration_last_date > start_date:
                raise serializers.ValidationError("Registration date cannot be after start date.")
            if not registration_last_date:
                raise serializers.ValidationError("Registration last date is required.")
            registration_link = data.get("registration_link")
            if not registration_link:
                raise serializers.ValidationError("Registration link is required.")
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["start_time"] = start_time
        data["end_time"] = end_time
        if not "contact_person" in data:
            raise serializers.ValidationError("Contact person is required.")
        contact_person = data.get("contact_person", [])
        if not contact_person or not isinstance(contact_person, list) or len(contact_person) < 1:
            raise serializers.ValidationError("At least one contact person is required.")
        for item in contact_person:
            image = item.get("photo")
            if isinstance(image, str) or image in ['null', 'None', 'undefined']:
                item.pop("photo")
        return data

    def handle_contact_person(self, contact_persons_data, event):
        """Handles adding, updating, and removing contact persons for an event."""

        existing_contacts = EventContactPerson.objects.filter(event=event)
        existing_contacts_dict = {contact.id: contact for contact in existing_contacts}
        to_keep_ids = set()

        for item in contact_persons_data:
            try:
                contact_id = int(item.get("id"))  # Extract ID if provided
                to_keep_ids.add(contact_id)
            except (TypeError, ValueError):
                contact_id = None
            item["event"] = event.id
            if contact_id and contact_id in existing_contacts_dict:
                # Update existing contact person
                contact_instance = existing_contacts_dict[contact_id]
                contact_serializer = EventContactPersonSerializer(contact_instance, data=item, partial=True)
                contact_serializer.is_valid(raise_exception=True)
                contact_serializer.save()
            else:
                # Create new contact person
                contact_serializer = EventContactPersonSerializer(data=item)
                contact_serializer.is_valid(raise_exception=True)
                new_contact = contact_serializer.save()
                to_keep_ids.add(new_contact.id)

        # Remove contact persons that are no longer referenced
        for contact in existing_contacts:
            if contact.id not in to_keep_ids:
                contact.delete()

    @extend_schema(tags=["Event"], examples=[
        OpenApiExample(
            "Create Event",
            value={
                  "contact_person": [
                    {
                      "name": "string",
                      "position": "string",
                      "email": "user@example.com",
                      "contact_number": "string",
                      "wa_number": "string",
                      "company": "string",
                      "whatsapp_available": True,
                      "language": "string",
                      "photo": "string",
                    }
                  ],
                  "title": "string",
                  "description": "string",
                  "start_date": "2025-03-19",
                  "end_date": "2025-03-19",
                  "is_all_day": True,
                  "start_time": "string",
                  "end_time": "string",
                  "event_image": "string",
                  "event_video": "string",
                  "event_type": "online",
                  "registration_available": True,
                  "registration_last_date": "2025-03-19",
                  "registration_link": "string",
                  "category": [
                    "real_estate"
                  ],
                  "sub_category": [
                    "property_showcase_launch"
                  ],
                  "meeting_link": "string",
                  "country": "string",
                  "district": "string",
                  "city": "string",
                  "location": "string",
                  "location_link": "string",
                  "text_color": "string",
                  "bg_color": "string",
                },
            request_only=True,
        )
    ], )
    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        validated_data = self.validate_data(request.data.copy())
        contact_person_data= validated_data.pop("contact_person")
        serializer = self.get_serializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # store the contact person information
        self.handle_contact_person(contact_person_data, instance)
        return Response(
            {"message": "Event created successfully"},
            status.HTTP_201_CREATED
        )

    @extend_schema(tags=["Event"], examples=[
        OpenApiExample(
            "Update Event",
            value={
                "contact_person": [
                    {
                        "id": "int",
                        "name": "string",
                        "position": "string",
                        "email": "user@example.com",
                        "contact_number": "string",
                        "wa_number": "string",
                        "company": "string",
                        "whatsapp_available": True,
                        "language": "string",
                        "photo": "string",
                    }
                ],
                "title": "string",
                "description": "string",
                "start_date": "2025-03-19",
                "end_date": "2025-03-19",
                "is_all_day": True,
                "start_time": "string",
                "end_time": "string",
                "event_image": "string",
                "event_video": "string",
                "event_type": "online",
                "registration_available": True,
                "registration_last_date": "2025-03-19",
                "registration_link": "string",
                "category": [
                    "real_estate"
                ],
                "sub_category": [
                    "property_showcase_launch"
                ],
                "meeting_link": "string",
                "country": "string",
                "district": "string",
                "city": "string",
                "location": "string",
                "location_link": "string",
                "text_color": "string",
                "bg_color": "string",
            },
            request_only=True,
        )
    ], )
    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception as e:
            if e.__class__.__name__ == "Http404":
                raise ObjectDoesNotExist(e)
            else:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = self.validate_data(request.data.dict())
        contact_person_data = validated_data.pop("contact_person")
        serializer = self.get_serializer(instance, data=validated_data)
        serializer.is_valid(raise_exception=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        obj.status = EventStatus.PENDING.value
        obj.save()
        self.handle_contact_person(contact_person_data, obj)
        return Response({"message": "Event updated successfully"}, status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        request.query_params._mutable = True
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["Event"], parameters=set_query_params(
        'list', [
            {"name": "date", 'description': "The number of the date of the event"},
            {"name": "week", 'description': "The number of the week of the event"},
            {"name": "month", 'description': "The number of the month of the event"},
            {"name": "year", 'description': "The year of the event"},
            {"name": "city", 'description': "The city of the event"},
            {"name": "district", 'description': "The district of the event"},
            {"name": "country", 'description': "The country of the event"},
            {"name": "event_date", 'description': "The filterable date of the event"},
            {"name": "category", 'description': "The status of the event", "enum": EventCategoryEnum.values()},
            {"name": "sub_category", "type":"list", 'description': "The status of the event", "enum": EventSubCategoryEnum.values()},
            {"name": "status", 'description': "The status of the event", "enum": EventStatus.values()},
        ]))
    @action(detail=False, methods=["GET"], url_path="calender")
    def calender_view(self, request, *args, **kwargs):
        today = now().date()
        date = request.query_params.get("date", None)
        week = request.query_params.get("week", None)
        month = int(request.query_params.get("month", today.month))
        year = int(request.query_params.get("year", today.year))
        city = request.query_params.get("city", None)
        district = request.query_params.get("district", None)
        country = request.query_params.get("country",None)
        category = request.query_params.get("category",None)
        sub_category = request.query_params.get("sub_category",None)
        event_date = request.query_params.get("event_date",None)
        if event_date and (month or year):
            month = None
            year = None
        status = request.query_params.get("status",None)

        # Convert `date` to an actual date object if provided
        if date:
            try:
                date = dt(year, month, int(date))  # Convert integer day to a full date
            except ValueError:
                return Response({"error": "Invalid date provided"}, status=400)

        # Build Query Filters
        filters = Q()
        if date:
            filters &= Q(start_date=date) | Q(end_date=date)
        if week:
            filters &= Q(start_date__week=week, start_date__year=year) | Q(end_date__week=week, end_date__year=year)
        if month:
            filters &= Q(start_date__month=month, start_date__year=year) | Q(end_date__month=month, end_date__year=year)
        if city:
            filters &= Q(city=city)
        if district:
            filters &= Q(district=district)
        if country:
            filters &= Q(country=country)
        if status:
            filters &= Q(status=status)
        if event_date:
            filters &= Q(start_date__lte=event_date, end_date__gte=event_date)
        if category:
            filters &= Q(category__contains=[category]) & ~Q(category=[]) & ~Q(category__isnull=True)
        if sub_category:
            sub_category_list = [item.strip() for item in sub_category.split(",")]  # Clean spaces
            sub_category_filters = reduce(or_, [Q(sub_category__overlap=[q]) for q in sub_category_list])
            filters &= sub_category_filters & ~Q(sub_category=[]) & ~Q(sub_category__isnull=True)

        # Fetch filtered events
        qs = self.model_class.active_objects.filter(filters)

        return Response( self.serializer_class(qs, many=True, context={"request": request}).data)
