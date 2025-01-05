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

    def __str__(self):
        return f"User: {self.user.username}. Trip: {self.trip}"

    def create_ticket(self):
        ticket = {
            "seat": self.seat.number,
            "price": self.seat.price,
            "town_from": self.trip.town_from,
            "town_to": self.trip.town_to,
            "time_out": self.trip.time_out,
            "time_in": self.trip.time_in,
            "airport": self.trip.airport,
        }
        return ticket


class Payment(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking"
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"User: {self.user.username}. Seat: {self.booking.seat}"
