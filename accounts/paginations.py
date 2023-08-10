from rest_framework.pagination import PageNumberPagination


class AccountsPagination(PageNumberPagination):
    page_size = 10
