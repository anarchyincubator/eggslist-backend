from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class PageNumberPaginationWithCount(pagination.PageNumberPagination):
    page_size = 12

    def get_paginated_response(self, data):
        return Response(self.get_paginated_dict(data))

    def get_paginated_dict(self, data):
        return OrderedDict(
            [
                ("total_pages", self.page.paginator.num_pages),
                ("count", self.page.paginator.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )
