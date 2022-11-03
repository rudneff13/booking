from django.db import models


class Rental(models.Model):
    """Model represents real estate entities"""
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'rental'
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'

    def __str__(self):
        return f"{self.id}: {self.name}"


class Reservation(models.Model):
    """Model for tracking Renal bookings"""
    rental = models.ForeignKey(Rental, related_name='reservations', on_delete=models.CASCADE)
    checkin = models.DateField()
    checkout = models.DateField()

    class Meta:
        db_table = 'reservation'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        indexes = [
            models.Index(fields=['checkout']),
        ]

    def __str__(self):
        return f"{self.id}: {self.rental.name}: {self.checkin}-{self.checkout}"
