from rest_framework.pagination import PageNumberPagination


class CompletedPagination(PageNumberPagination):
    page_size = 18


class PostPagination(PageNumberPagination):
    page_size = 20
