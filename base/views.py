import json
import hashlib
from typing import Dict, Any
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import ValidationError


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from base.helpers import calculate_seconds_until_end_of_day


class CustomViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = (AllowAny,)
    periodic_delete_enabled = False
    cache_prefix = []
    cache_key = ""
    model_class = None
    filterset_class = None  # Set this to a FilterSet class in subclasses
    search_fields = []
    filter_backends = [DjangoFilterBackend, SearchFilter]

    @staticmethod
    def max_cache_time():
        return calculate_seconds_until_end_of_day()

    @staticmethod
    def filterable_cache_key(prefix: Dict[str, str], filters: Dict[str, Any]) -> str:
        """
        Generate a cache key based on filters and pagination params.
        """
        page_number = filters.get("page_number", 1)
        page_size = filters.get("page_size", 10)

        # Validate prefix
        if not isinstance(prefix, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in prefix.items()
        ):
            raise ValidationError("Prefix must be a dictionary with string keys and values.")

        # Validate filters
        if not isinstance(filters, dict) or not all(isinstance(k, str) for k in filters.keys()):
            raise ValidationError("Filters must be a dictionary with string keys.")

        # Create a hash of sorted filters
        filter_str = json.dumps(filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode("utf-8")).hexdigest()

        # Prefix validation
        if "name" not in prefix:
            raise ValidationError("Prefix dictionary must include a 'name' key.")

        prefix_name = "_".join(f"{v}" for k, v in prefix.items())
        return f"{prefix_name}_{filter_hash}_page_{page_number}_size_{page_size}"

    def get_queryset(self):
        queryset = self.get_base_queryset()

        if self.filterset_class:
            filterset = self.filterset_class(data=self.request.query_params, queryset=queryset, request=self.request)
            if filterset.is_valid():
                queryset = filterset.qs
            else:
                raise ValidationError(filterset.errors)

        return queryset.order_by("-created_at")

    def get_base_queryset(self):
        obj_type = self.request.query_params.get("is_active", "true").lower()
        model = self.model_class

        if self.action == "retrieve":
            return model.objects

        if obj_type == "true":
            queryset = model.active_objects
        elif obj_type == "false":
            queryset = model.inactive_objects
        else:
            queryset = model.objects

        # Apply optimizations
        return self.apply_relational_optimizations(queryset)

    def apply_relational_optimizations(self, queryset):
        info = CacheManager.get_cache("model_info", {}).get(self.model_class.__name__.lower(), {})
        if not info:
            info = CacheManager.update_model_info_in_cache(self.model_class)

        if info.get("select_related"):
            queryset = queryset.select_related(*info["select_related"])
        if info.get("prefetch_related"):
            queryset = queryset.prefetch_related(*info["prefetch_related"])
        return queryset

    # def clear_cache(self):
    #     if isinstance(self.cache_prefix, list):
    #         for prefix in self.cache_prefix:
    #             CacheManager.clear_cache_with_prefix(prefix)
    #     else:
    #         CacheManager.clear_cache_with_prefix(self.cache_prefix)

    def create(self, request, *args, **kwargs):
        # self.clear_cache()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # self.clear_cache()
        return super().update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=str,
                required=False,
                description="Filter by active status. Allowed values: 'true', 'false', 'any'.",
                enum=["true", "false", "any"],  # Enum to restrict allowed values
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        # filters = request.query_params.dict()
        # cache_key = self.filterable_cache_key(prefix={"name": self.cache_key}, filters=filters)
        #
        # data = CacheManager.get_cache(cache_key)
        # if not data:
        data = super().list(request, *args, **kwargs).data
        # if isinstance(data, list):
        #     CacheManager.set_cache(cache_key, data, self.max_cache_time())
        # else:
        #     if data.get("results", []):
        #         CacheManager.set_cache(cache_key, data, self.max_cache_time())
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # cache_key = f"{self.cache_key}_{kwargs.get(self.lookup_field)}"
        # data = CacheManager.get_cache(cache_key)
        # if not data:
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            # CacheManager.set_cache(cache_key, data, self.max_cache_time())
        except Exception as e:
            if e.__class__.__name__ == "Http404":
                raise ObjectDoesNotExist(e)
            else:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Perform a natural (hard) delete of the resource.
        """
        try:
            response = super().destroy(request, *args, **kwargs)
            # self.clear_cache()
            return response
        except Exception as e:
            if e.__class__.__name__ == "Http404":
                raise ObjectDoesNotExist(e)
            else:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

