from django.urls import path

from rent.views import RentalViewSet, ReservationViewSet

urlpatterns = [
    path('rentals/', RentalViewSet.as_view({'get': 'list', 'post': 'create'}), name='rentals'),
    path('rentals/<int:pk>', RentalViewSet.as_view({'delete': 'destroy', 'get': 'retrieve'}), name='rental'),

    path('reservations/', ReservationViewSet.as_view({'post': 'create', 'get': 'list'}), name='reservations'),
    path('reservations/<int:pk>', ReservationViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy', 'put': 'update'}
    ), name='reservation'),
]
