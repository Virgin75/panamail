from rest_framework import pagination

class x20ResultsPerPage(pagination.PageNumberPagination):
    page_size = 20
    page_query_param = 'p'