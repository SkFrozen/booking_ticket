import stripe
from django.http import FileResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app.forms import PassportForm, PassportFormSet
from app.models import Booking, Passport, Payment
from trips.models import Airport, City, Company, Country, Plane, Seat, Trip
from users.models import User


class TestAppViews(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="test", email="test@test.com", password="test"
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
        cls.booked_seat = Seat.objects.create(
            number="33A",
            is_booked=True,
            trip=cls.trip,
            price=150,
            seat_class="economy",
        )
        cls.seat = Seat.objects.create(
            number="33B",
            trip=cls.trip,
            price=150,
            seat_class="economy",
        )
        cls.payment_1 = Payment.objects.create()
        cls.payment_2 = Payment.objects.create()
        cls.passport_1 = Passport.objects.create(
            email="test@test.com",
            number="123456789",
            nationality="BY",
            first_name="test",
            last_name="test_last",
            date_of_birth="1994-03-12",
            sex="male",
        )
        cls.passport_2 = Passport.objects.create(
            email="test@test.com",
            number="123456ter789",
            nationality="RU",
            first_name="test_2",
            last_name="test_last_@",
            date_of_birth="1998-03-12",
            sex="female",
            owner=cls.user,
        )

        cls.booking = Booking.objects.create(
            seat=cls.booked_seat,
            payment=cls.payment_2,
            passport=cls.passport_2,
        )

    def test_ticket_download_view(self):
        self.client.force_login(self.user)
        url = reverse("download_ticket", kwargs={"booking_id": self.booking.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIsInstance(response, FileResponse)

    def test_passport_create_view_auth_user(self):
        self.client.force_login(self.user)
        url = reverse("passport_create", kwargs={"trip_id": self.trip.id})
        # request method GET
        response = self.client.get(url)
        formset = response.context["formset"]

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(formset, PassportFormSet)

        # request method POST
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-0-email": "test@test.com",
            "form-0-number": "PU156781NK",
            "form-0-nationality": "BY",
            "form-0-first_name": "test_func",
            "form-0-last_name": "test_last_func",
            "form-0-date_of_birth": "1997-03-12",
            "form-0-sex": "male",
            "form-1-email": "test@test2.com",
            "form-1-number": "PU156781NK123",
            "form-1-nationality": "BY",
            "form-1-first_name": "test_func_2",
            "form-1-last_name": "test_last_func_2",
            "form-1-date_of_birth": "1991-03-12",
            "form-1-sex": "female",
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)

        passport_1 = Passport.objects.filter(number="PU156781NK").first()
        passport_2 = Passport.objects.filter(number="PU156781NK123").first()

        self.assertEqual(passport_1.number, "PU156781NK")
        self.assertEqual(passport_1.owner, self.user)
        self.assertEqual(passport_2.number, "PU156781NK123")
        self.assertEqual(passport_2.owner, self.user)

    def test_passport_update_view_auth_user(self):
        self.client.force_login(self.user)
        url = reverse("passport_update", kwargs={"passport_id": self.passport_2.id})
        # request method GET
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertIsInstance(form, PassportForm)
        self.assertEqual(form.initial["number"], self.passport_2.number)
        # request method POST
        data = form.initial
        data["first_name"] = "update_test"
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)

        passport = Passport.objects.filter(number=self.passport_2.number).first()

        self.assertEqual(passport.first_name, "update_test")

    def test_booking_passports_view_auth_user(self):
        self.client.force_login(self.user)
        url = reverse("passports_list", kwargs={"trip_id": self.trip.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/passport_list.html")
        self.assertIsNotNone(response.context.get("passports"))

        trip = response.context["trip"]
        seats_map: dict = response.context["seats_map"]
        passports = response.context["passports"]

        self.assertEqual(trip.id, self.trip.id)
        self.assertIsInstance(seats_map, dict)
        self.assertIsNotNone(seats_map.get("business"))
        self.assertIsNotNone(seats_map.get("economy"))
        self.assertEqual(len(seats_map["business"]), 2)
        self.assertEqual(len(seats_map["economy"]), 3)
        self.assertEqual(len(seats_map["business"][1]), 4)
        self.assertEqual(len(seats_map["economy"][3]), 4)
        self.assertEqual(len(passports), 1)
        self.assertEqual(passports[0].owner, self.user)

    def test_booking_passports_view_anonymous(self):
        url = reverse("passports_list", kwargs={"trip_id": self.trip.id})
        response = self.client.get(url)

        self.assertIsNotNone(response.context.get("formset"))

        formset = response.context.get("formset")

        self.assertIsInstance(formset, PassportFormSet)

    def test_booking_seat_view_auth_user(self):
        self.client.force_login(self.user)
        url = reverse("book_seat", kwargs={"trip_id": self.trip.id})
        response = self.client.get(
            url, data={"seat": [self.seat.id], "passport": self.passport_2.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/success-booking.html")
        self.assertIsNotNone(response.context.get("info_book"))

        info_book = response.context["info_book"]

        payment_id = info_book["payment_id"]
        payment = Payment.objects.filter(id=payment_id).first()

        self.assertIsNotNone(payment)
        self.assertFalse(payment.paid)

        booking = payment.booking.all().first()
        seat = booking.seat

        self.assertIsNotNone(booking)
        self.assertEqual(booking.passport, self.passport_2)
        self.assertTrue(seat.is_booked)
        self.assertEqual(info_book["cost"], 150)
        self.assertEqual(info_book["seats"], 1)

        stripe_session_id = info_book["stripe_session_id"]
        stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)

        self.assertIsInstance(stripe_session, stripe.checkout.Session)

    def test_booking_seat_view_anonymous(self):
        url = reverse("book_seat", kwargs={"trip_id": self.trip.id})
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-0-email": "test@test.com",
            "form-0-number": "123456789",
            "form-0-nationality": "BY",
            "form-0-first_name": "test",
            "form-0-last_name": "test_last",
            "form-0-date_of_birth": "1994-03-12",
            "form-0-sex": "male",
            "seat": [self.seat.id],
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context.get("info_book"))

    def test_booking_seat_view_anonymous_invalid_data(self):
        url = reverse("book_seat", kwargs={"trip_id": self.trip.id})
        # this passport exists in the database
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-0-email": "test@test.com",
            "form-0-number": "123456789",
            "form-0-nationality": "BY",
            "form-0-first_name": "else name",  # wrong first name
            "form-0-last_name": "last else name",  # wrong last name
            "form-0-date_of_birth": "1994-03-12",
            "form-0-sex": "male",
            "seat": [self.seat.id],
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error: Check the entered data", response.content.decode())

    def test_booking_seat_view_anonymous_incorrect_number_seats(self):
        url = reverse("book_seat", kwargs={"trip_id": self.trip.id})
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-0-email": "test@test.com",
            "form-0-number": "123456789ETW",
            "form-0-nationality": "BY",
            "form-0-first_name": "else name",
            "form-0-last_name": "last else name",
            "form-0-date_of_birth": "1994-03-12",
            "form-0-sex": "male",
            "seat": [self.seat.id, self.booked_seat.id],
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error: Incorrect number of seats", response.content.decode())
