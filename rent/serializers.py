from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField
from rest_framework.serializers import ModelSerializer

from rent.models import Rental, Reservation


class RentalSerializer(ModelSerializer):
    """General Rental serializer"""
    class Meta:
        model = Rental
        fields = '__all__'


class ReservationListSerializer(ModelSerializer):
    """Reservation serializer for list view"""
    rental_name = CharField(source="rental.name", max_length=128, read_only=True)
    previous_reservation = IntegerField(allow_null=True, read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "rental_name",
            "id",
            "checkin",
            "checkout",
            "previous_reservation"
        ]
        read_only_fields = fields


class ReservationSerializer(ModelSerializer):
    """Reservation serializer for create method"""

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate(self, attrs):
        checkout = attrs.get('checkout')
        checkin = attrs.get('checkin')
        if checkout < checkin:
            raise ValidationError("Checkout date should be equal or after checking date")

        existing_bookings = Reservation.objects.filter(rental_id=attrs.get('rental'), checkout__gte=checkin).\
            filter(checkin__lte=checkout)
        if existing_bookings.exists():
            raise ValidationError("Date is busy! Choose another date!")
        return attrs
