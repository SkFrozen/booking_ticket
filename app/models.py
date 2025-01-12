from typing import Any

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django_countries.fields import CountryField

from trips.models import Seat

cipher_sisuite = Fernet(settings.ENCRYPTION_KEY.encode())


class Passport(models.Model):
    SEX_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
    )

    number = models.CharField(max_length=120)
    nationality = CountryField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    owner = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        related_name="passports",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "passports"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = cipher_sisuite.encrypt(self.number.encode()).decode()
        super().save(*args, **kwargs)

    @property
    def get_number(self) -> str:
        return cipher_sisuite.decrypt(self.number.encode()).decode()


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("rejected", "Rejected"),
    )

    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name="seat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="pending")
    passport = models.ForeignKey(Passport, on_delete=models.CASCADE)

    class Meta:
        db_table = "booking"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Seat: {self.seat}"

    @property
    def ticket(self) -> dict[str, Any]:
        ticket = {
            "seat": self.seat.number,
            "price": self.seat.price,
            "town_from": self.seat.trip.departure_airport.city.name,
            "airport_from": self.seat.trip.departure_airport.name,
            "town_to": self.seat.trip.arrival_airport.city.name,
            "airport_to": self.seat.trip.arrival_airport.name,
            "time_out": self.seat.trip.time_out,
            "time_in": self.seat.trip.time_in,
        }
        return ticket


class Payment(models.Model):
    booking = models.ManyToManyField(Booking, related_name="payment")
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.paid} {self.booking}"
