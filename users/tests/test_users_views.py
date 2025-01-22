from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlencode, urlsafe_base64_encode

from app.models import Booking, Passport, Payment
from trips.models import Airport, City, Company, Country, Plane, Seat, Trip

from ..models import User


class TestRegisterViews(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.url = reverse("register")
        cls.user_data = {
            "username": "test",
            "email": "test@test.com",
            "password": "test",
            "password2": "test",
            "date_of_birth": "03/20/1990",
        }
        cls.user = User.objects.create_user(
            username="confirm_test",
            email="confirm@test.com",
            password="test",
            date_of_birth="1990-03-20",
            is_active=False,
        )

    def test_register(self) -> None:
        response = self.client.post(self.url, self.user_data)
        user = User.objects.get(username="test")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertEqual(user.is_active, False)

    def test_register_invalid_data(self) -> None:
        self.user_data["username"] = ""

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register-form.html")
        self.assertFormError(response, "form", "username", "This field is required.")

    def test_confirm_register_view(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(str(self.user.username)))
        token = default_token_generator.make_token(self.user)
        self.url = reverse("register_confirm", args=(uidb64, token))

        response = self.client.get(self.url)
        user = User.objects.get(username=self.user.username)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.is_active, True)
        self.assertRedirects(response, reverse("login"))


class TestProfileView(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.url = reverse("profile")
        cls.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            password="test",
            date_of_birth="1990-03-20",
        )
        cls.company = Company.objects.create(name="test_company", code="TC")
        cls.country = Country.objects.create(name="test_country")
        cls.city = City.objects.create(name="test_city", country=cls.country)
        cls.airport = Airport.objects.create(name="test_airport", city=cls.city)
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
        cls.trip = Trip.objects.create(
            number="TC-6563",
            time_out=timezone.now() + timezone.timedelta(days=1),
            time_in=timezone.now() + timezone.timedelta(days=1, hours=5),
            departure_airport=cls.airport,
            arrival_airport=cls.airport,
            plane=cls.plane,
            company=cls.company,
        )
        cls.seat = Seat.objects.create(
            number="A10",
            trip=cls.trip,
            is_booked=True,
            price=150,
            seat_class="economy",
        )
        cls.passport = Passport.objects.create(
            email="test@test.com",
            number="123456789",
            nationality="BY",
            date_of_birth="1990-03-20",
            sex="male",
            first_name="test",
            last_name="test_last",
            owner=cls.user,
        )
        cls.payment = Payment.objects.create()
        cls.booking = Booking.objects.create(
            seat=cls.seat, passport=cls.passport, payment=cls.payment
        )

    def test_profile_view(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        passports = response.context[0]["passports"]
        bookings = response.context[0]["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(passports), 1)
        self.assertEqual(len(bookings), 1)
        self.assertEqual(passports[0], self.passport)
        self.assertEqual(passports[0].owner, self.user)
        self.assertEqual(bookings[0]["trip_number"], "TC-6563")
        self.assertEqual(bookings[0]["departure_city"], "test_city")
        self.assertEqual(bookings[0]["arrival_city"], "test_city")
        self.assertEqual(bookings[0]["departure_airport"], "test_airport")
        self.assertEqual(bookings[0]["arrival_airport"], "test_airport")
        self.assertEqual(bookings[0]["first_name"], "test")
        self.assertEqual(bookings[0]["last_name"], "test_last")
        self.assertEqual(bookings[0]["seat_number"], "A10")
        self.assertEqual(bookings[0]["price"], 150)
        self.assertEqual(bookings[0]["status"], "pending")
