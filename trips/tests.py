from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Airport, City, Company, Country, Plane, Trip


class TestTrip(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.company = Company.objects.create(name="test_company", code="TC")
        cls.country_1 = Country.objects.create(name="test_country")
        cls.country_2 = Country.objects.create(name="country_test")
        cls.city_1 = City.objects.create(name="test_city", country=cls.country_1)
        cls.city_2 = City.objects.create(name="city_test", country=cls.country_2)
        cls.airport_1 = Airport.objects.create(name="test_airport", city=cls.city_1)
        cls.airport_2 = Airport.objects.create(name="airport_test", city=cls.city_2)
        cls.plane = Plane.objects.create(
            model="test_plane",
            seat_configuration={
                "business_rows": 2,
                "business_seats_per_row": 4,
                "economy_rows": 2,
                "economy_seats_per_row": 4,
            },
            business_class_price=250,
            economy_class_price=150,
        )
        cls.trip_1 = Trip.objects.create(
            number="TC-6563",
            time_out=timezone.now() + timezone.timedelta(days=1),
            time_in=timezone.now() + timezone.timedelta(days=1, hours=5),
            departure_airport=cls.airport_1,
            arrival_airport=cls.airport_2,
            plane=cls.plane,
            company=cls.company,
        )
        cls.trip_2 = Trip.objects.create(
            number="TC-666",
            time_out=timezone.now() + timezone.timedelta(days=1),
            time_in=timezone.now() + timezone.timedelta(days=1, hours=5),
            departure_airport=cls.airport_2,
            arrival_airport=cls.airport_1,
            plane=cls.plane,
            company=cls.company,
        )

    def test_cities_list_view(self):
        response = self.client.get(
            reverse("cities_list", kwargs={"country_id": self.country_1.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/cities_list.html")

        page = response.context[0]["page_obj"]

        self.assertIsInstance(page, Page)
        self.assertEqual(page.has_next(), False)
        self.assertEqual(page.start_index(), 1)

        city = response.context[0]["page_obj"][0]

        self.assertEqual(city.name, "test_city")
        self.assertEqual(city.country, self.country_1)

    def test_trips_list_view(self):
        response = self.client.get(
            reverse(
                "trips_list",
                kwargs={
                    "country_id": self.country_2.id,
                    "city_id": self.city_2.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_list.html")

        page = response.context[0]["page_obj"]

        self.assertIsInstance(page, Page)
        self.assertEqual(page.has_next(), False)
        self.assertEqual(page.start_index(), 1)

        trip = page[0]

        self.assertEqual(trip, self.trip_1)

    def test_trips_search_list_view(self):
        response = self.client.get(
            reverse("search_trips"), data={"arrival_city": "test_city"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_list.html")

        not_page = response.context[0]["page_obj"]
        self.assertNotIsInstance(not_page, Page)

        trip = not_page[0]

        self.assertEqual(trip, self.trip_2)

        response = self.client.get(reverse("search_trips"))
        self.assertEqual(response.status_code, 302)

    def test_signal_country_changes_delete_cache(self):
        response = self.client.get(reverse("directions"))

        self.assertEqual(len(cache.get("countries")), 2)

        self.country_1.name = "France"
        self.country_1.save()

        self.assertEqual(cache.get("countries"), None)
