from random import randint

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from trips.models import Company, Country, Seat, Trip
from users.models import User

from .models import Booking, Payment


class TestBookingView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="test_password",
            date_of_birth="2000-01-01",
        )

        cls.company = Company.objects.create(name="Test Company")
        cls.country = Country.objects.create(name="Test Country")

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
                country=cls.country,
            )
            for i in range(1, 3)
        ]
        cls.seats = [
            Seat.objects.create(
                number=i,
                price=300,
                trip=cls.trip[randint(0, 1)],
            )
            for i in range(1, 101)
        ]

    def setUp(self):
        self.trip_id = self.trip[randint(0, 1)].id
        self.booked_seats = Seat.objects.filter(trip_id=self.trip_id).order_by("id")
        self.url = reverse("booking", args=[self.trip_id])
        self.client.force_login(self.user)

    def test_booking_seats_chart(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        seats = Trip.objects.get(id=self.trip_id).seats.all().order_by("id")

        self.assertQuerySetEqual(
            seats, response.context["seats"], ordered=True, msg="Seats are not equal"
        )

    def test_booking_seat(self):
        self.url = reverse("book_seat", args=[self.trip_id])
        seats_id = [seat.id for seat in self.booked_seats][0:3]
        response = self.client.get(self.url, data={"seat": seats_id})

        self.assertEqual(response.status_code, 200)
        self.assertIn("info_book", response.context)

        seats = Seat.objects.filter(id__in=seats_id).filter(is_booked=True).all()
        booking = Booking.objects.filter(user=self.user).filter(seat__in=seats).all()

        total_price = response.context["info_book"]["total_price"]
        total_seats = response.context["info_book"]["total_seats"]
        trip_id = response.context["info_book"]["trip_id"]

        self.assertTrue(booking.exists())
        self.assertEqual(trip_id, self.trip_id)
        self.assertEqual(len(seats), total_seats)
        self.assertEqual(900, total_price)

    def test_seats_is_none(self):
        self.url = reverse("book_seat", args=[self.trip_id])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


class TestPaymentView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="test_password",
            date_of_birth="2000-01-01",
        )
        cls.company = Company.objects.create(name="Test Company")
        cls.country = Country.objects.create(name="Test Country")

        cls.time_out = timezone.now() + timezone.timedelta(days=3)
        cls.time_in = cls.time_out + timezone.timedelta(hours=5)
        cls.trip = Trip.objects.create(
            town_from="test_town_from",
            town_to="test_town_to",
            airport="test_airport",
            plane="test_plane",
            time_out=cls.time_out,
            time_in=cls.time_in,
            company=cls.company,
            country=cls.country,
        )

        cls.seats = [
            Seat.objects.create(
                number=i,
                price=300,
                trip=cls.trip,
                is_booked=True,
            )
            for i in range(1, 4)
        ]
        cls.booking = [
            Booking.objects.create(user=cls.user, seat=seat, trip=cls.trip)
            for seat in cls.seats
        ]

    def setUp(self):
        self.booking_id = self.booking[randint(0, 3)].id
        self.url = reverse("payment", args=[self.booking_id])
        self.client.force_login(self.user)

    def test_payment(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("msg", response.context)

        booking = Booking.objects.get(id=self.booking_id, paid=True)
        payment = Payment.objects.filter(user=self.user, booking=booking)

        self.assertTrue(booking.paid)
        self.assertTrue(payment.exists)
