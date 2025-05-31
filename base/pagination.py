from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return page_number

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        return page_number

    def get_total_pages(self):
        page_size = self.request.query_params.get(
            self.page_size_query_param, self.page_size
        )
        page_size = int(page_size) if page_size else self.page_size
        total_items = self.page.paginator.count
        return ceil(total_items / page_size)

    def get_current_page(self):
        return self.page.number

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.get_total_pages(),
                "current_page": self.get_current_page(),
                "results": data,
            }
        )
