from django.contrib import admin

from rent.models import Rental, Reservation

admin.site.register(Rental)
admin.site.register(Reservation)
