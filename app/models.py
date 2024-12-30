from django.contrib.auth import get_user_model
from django.db import models

from trips.models import Seat, Trip


class Booking(models.Model):
    paid = models.BooleanField(default=False)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="seat")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user"
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking"
        ordering = ["-created_at"]


class Payment(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking"
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
