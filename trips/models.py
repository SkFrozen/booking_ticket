from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "countries"
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name


class Trip(models.Model):
    town_from = models.CharField(max_length=100)
    town_to = models.CharField(max_length=100)
    airport = models.CharField(max_length=100)
    plane = models.CharField(max_length=20)
    time_out = models.DateTimeField()
    time_in = models.DateTimeField()
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="company"
    )
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "trips"
        verbose_name_plural = "trips"

    def __str__(self) -> str:
        return f"{self.id}: {self.town_from} - {self.town_to}"

    @property
    def free_seats_count(self) -> int:
        return self.seats.filter(is_booked=False).count()


class Seat(models.Model):
    number = models.CharField(max_length=10)
    price = models.IntegerField()
    is_booked = models.BooleanField(default=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="seats")

    @property
    def count(self) -> int:
        return Seat.objects.filter(trip=self.trip).count()

    def __str__(self) -> str:
        return f"Trip: {self.trip.id}. Number: {self.number}"
