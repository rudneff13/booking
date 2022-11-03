from drf_yasg2.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from rent.models import Rental, Reservation
from rent.serializers import RentalSerializer, ReservationListSerializer, ReservationSerializer


class RentalViewSet(ModelViewSet):
    serializer_class = RentalSerializer
    queryset = Rental.objects.all()
    http_method_names = ['get', 'post', 'delete']


class ReservationResultsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5


class ReservationViewSet(ModelViewSet):
    serializer_class = ReservationSerializer
    http_method_names = ['get', 'delete', 'put', 'post']
    queryset = Reservation.objects.all()
    pagination_class = ReservationResultsPagination

    def get_queryset(self):
        # select from two tables with a single query
        qs = Reservation.objects.all().select_related("rental").order_by("rental__name", "checkout")
        qs_length = len(qs)
        if qs_length:
            qs[0].previous_reservation = None
            # iterate over queryset: if next item has the same rental.id as a previous one
            #   then add "previous_reservation".
            # iterating over qs only once: time complexity is O(n); 0 extra requests to db -- success!
            for index in range(1, qs_length):
                if qs[index].rental.id == qs[index-1].rental.id:
                    qs[index].previous_reservation = qs[index-1].id
                else:
                    qs[index].previous_reservation = None
        return qs

    @swagger_auto_schema(
        operation_description="""Displays Reservations list with the previous reservation info""",
        responses={
            status.HTTP_200_OK: ReservationListSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReservationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReservationListSerializer(queryset, many=True)
        return Response(serializer.data)
