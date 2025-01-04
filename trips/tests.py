from datetime import datetime
from random import randint

from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Company, Country, Trip


class TestTripViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.company = Company.objects.create(name="Test Company")
        cls.countries = [
            Country.objects.create(name=f"Test Country{i}") for i in range(1, 5)
        ]
        cls.time_out = timezone.now() + timezone.timedelta(days=3)
        cls.time_in = cls.time_out + timezone.timedelta(hours=5)
        cls.trip = [
            Trip.objects.create(
                town_from=f"test_town_from_{i}",
                town_to=f"test_town_to_{i}",
                airport=f"test_airport_{i}",
                plane=f"test_plane_{i}",
                time_out=cls.time_out,
                time_in=cls.time_in,
                company=cls.company,
                country=cls.countries[randint(0, 3)],
            )
            for i in range(1, 26)
        ]

    def setUp(self):
        self.country = self.countries[randint(0, 3)]
        self.url = reverse("trip_list_by_direction", args=[self.country.id])

    def test_trip_list_by_direction(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip-list.html")
        self.assertIn("page_obj", response.context)

        res_trips = response.context["page_obj"].paginator.object_list
        trips = Trip.objects.filter(country=self.country).all()

        self.assertCountEqual(res_trips, trips)

    def test_trip_list_by_town_view(self):
        now = timezone.now()
        date_out = timezone.make_aware(
            datetime(now.year, now.month, now.day)
        ) + timezone.timedelta(days=1)

        trip = Trip.objects.filter(country=self.country, time_out__gt=date_out).first()

        url = reverse("detail_trip", args=[self.country.id, trip.town_to])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip-list.html")
        self.assertIn("page_obj", response.context)

        res_trips = response.context["page_obj"].paginator.object_list

        self.assertCountEqual(res_trips, [trip])
