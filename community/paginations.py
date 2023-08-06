from rest_framework.pagination import PageNumberPagination


class CompletedPagination(PageNumberPagination):
    page_size = 20
