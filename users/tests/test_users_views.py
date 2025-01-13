from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlencode, urlsafe_base64_encode

from app.models import Booking
from trips.models import Company, Country, Seat, Trip

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


# class TestProfileView(TestCase):

#     @classmethod
#     def setUpTestData(cls) -> None:
#         cls.client = Client()
#         cls.url = reverse("profile")
#         cls.user = User.objects.create_user(
#             username="test",
#             email="test@test.com",
#             password="test",
#             date_of_birth="1990-03-20",
#         )
#         cls.company = Company.objects.create(name="test_company")
#         cls.country = Country.objects.create(name="test_country")
#         cls.trip = Trip.objects.create(
#             town_from="test_town_from",
#             town_to="test_town_to",
#             time_out=timezone.now() + timezone.timedelta(days=5),
#             time_in=timezone.now() - timezone.timedelta(days=5, hours=5),
#             airport="test_airport",
#             plane="test_plane",
#             company=cls.company,
#             country=cls.country,
#         )
#         cls.seats = [
#             Seat.objects.create(price=100, trip=cls.trip, number=i, is_booked=True)
#             for i in range(5)
#         ]
#         cls.booking = [
#             Booking.objects.create(user=cls.user, trip=cls.trip, seat=seat)
#             for seat in cls.seats
#         ]

#     def test_profile_view(self) -> None:
#         self.client.force_login(self.user)
#         response = self.client.get(self.url)

#         res_users = [book.user for book in response.context[0].get("bookings")]
#         users = [book.user for book in self.booking]

#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "registration/profile.html")
#         self.assertCountEqual(res_users, users)
