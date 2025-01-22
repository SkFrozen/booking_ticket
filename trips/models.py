import string

from django.db import models
from django.utils.crypto import get_random_string


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=6)
    image = models.ImageField(upload_to="companies/", blank=True, null=True)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "companies"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="countries/", blank=True, null=True)

    class Meta:
        db_table = "countries"
        verbose_name_plural = "countries"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="cities/", blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    class Meta:
        db_table = "cities"
        verbose_name_plural = "cities"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="airports")

    class Meta:
        db_table = "airports"
        verbose_name_plural = "airports"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self) -> str:
        return self.name


class Plane(models.Model):
    model = models.CharField(max_length=100)
    seat_configuration = models.JSONField(default=dict)
    business_class_price = models.IntegerField(default=200)
    economy_class_price = models.IntegerField(default=100)

    class Meta:
        db_table = "planes"
        verbose_name_plural = "planes"
        indexes = [
            models.Index(fields=["model"]),
        ]

    def __str__(self) -> str:
        return self.model

    def create_seats(self, trip) -> None:
        seats = []
        config = self.seat_configuration

        business_rows = config.get("business_rows", 0)
        business_seats_per_row = config.get("business_seats_per_row", 0)
        economy_rows = config.get("economy_rows", 0) + business_rows
        economy_seats_per_row = config.get("economy_seats_per_row", 0)

        for row in range(1, business_rows + 1):
            for seat_number in range(1, business_seats_per_row + 1):
                number = f"{row}{chr(64 + seat_number)}"
                seat = Seat(
                    trip=trip,
                    number=number,
                    seat_class="business",
                    price=self.business_class_price,
                )
                seats.append(seat)

        for row in range(business_rows + 1, economy_rows + 1):
            for seat_number in range(1, economy_seats_per_row + 1):
                number = f"{row}{chr(64 + seat_number)}"
                seat = Seat(
                    trip=trip,
                    number=number,
                    seat_class="economy",
                    price=self.economy_class_price,
                )
                seats.append(seat)

        Seat.objects.bulk_create(seats)


class Trip(models.Model):
    number = models.CharField(max_length=10, unique=True, blank=True)
    departure_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_trips"
    )
    arrival_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_trips"
    )
    time_out = models.DateTimeField()
    time_in = models.DateTimeField()
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE, related_name="trips")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="trips")

    class Meta:
        db_table = "trips"
        verbose_name_plural = "trips"
        indexes = [
            models.Index(fields=["departure_airport"]),
            models.Index(fields=["arrival_airport"]),
            models.Index(fields=["time_out"]),
            models.Index(fields=["plane"]),
            models.Index(fields=["company"]),
            models.Index(fields=["number"]),
        ]

    def __str__(self) -> str:
        return self.number

    @property
    def free_seats_count(self) -> int:
        return self.seats.filter(is_booked=False).count()

    @property
    def time_on_way(self) -> str:
        hours, seconds = divmod((self.time_in - self.time_out).seconds, 3600)
        minutes = seconds // 60
        return f"{hours}h:{minutes}m"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_trip_number()
        super().save(*args, **kwargs)
        if not Seat.objects.filter(trip=self).exists():
            self.plane.create_seats(self)

    def _generate_trip_number(self) -> str:
        unique_id = get_random_string(4, allowed_chars=string.digits)
        return f"{self.company.code}-{unique_id}"


class Seat(models.Model):
    SEAT_CLASS_CHOICES = (
        ("business", "Business"),
        ("economy", "Economy"),
    )

    number = models.CharField(max_length=5)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="seats")
    is_booked = models.BooleanField(default=False)
    price = models.IntegerField()
    seat_class = models.CharField(max_length=8, choices=SEAT_CLASS_CHOICES)

    class Meta:
        db_table = "seats"
        verbose_name_plural = "seats"
        indexes = [
            models.Index(fields=["trip"]),
        ]

    @property
    def count(self) -> int:
        return Seat.objects.filter(trip=self.trip).count()

    def __str__(self) -> str:
        return self.number
