from django.test import Client, TestCase
from django.utils import timezone

from trips.models import Airport, City, Company, Country, Plane, Seat, Trip
from users.models import User

from ..models import Booking, Passport, Payment
from ..tasks import reject_booking_task


class TestAppTasks(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.user = User.objects.create(
            username="test_user",
            email="test@test.com",
            password="test_password",
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
            number="A33",
            trip=cls.trip,
            is_booked=True,
            seat_class="economy",
            price=150,
        )
        cls.payment = Payment.objects.create()
        cls.passport = Passport.objects.create(
            email="test@test.com",
            number="123456789",
            nationality="BY",
            first_name="test",
            last_name="test_last",
            date_of_birth="1994-03-12",
            sex="male",
        )
        cls.booking = Booking.objects.create(
            seat=cls.seat,
            payment=cls.payment,
            passport=cls.passport,
        )

    def test_reject_booking_task_paid_false_owner_none(self):
        reject_booking_task.apply(args=[self.payment.id])

        booking = Booking.objects.filter(pk=self.booking.id).first()
        passport = Passport.objects.filter(pk=self.passport.id).first()
        payment = Payment.objects.filter(pk=self.payment.id).first()
        seat = Seat.objects.filter(pk=self.seat.id).first()

        self.assertEqual(booking, None)
        self.assertEqual(seat.is_booked, False)
        self.assertEqual(passport, None)
        self.assertEqual(payment, None)

    def test_reject_booking_task_paid_false_owner_user(self):
        self.passport.owner = self.user
        self.passport.save()

        reject_booking_task.apply(args=[self.payment.id])

        booking = Booking.objects.filter(pk=self.booking.id).first()
        passport = Passport.objects.filter(pk=self.passport.id).first()
        payment = Payment.objects.filter(pk=self.payment.id).first()

        self.assertEqual(passport.owner, self.user)
        self.assertEqual(booking, None)
        self.assertEqual(payment, None)

    def test_reject_booking_task_paid_true(self):
        self.payment.paid = True
        self.payment.save()

        reject_booking_task.apply(args=[self.payment.id])

        booking = Booking.objects.filter(pk=self.booking.id).first()
        passport = Passport.objects.filter(pk=self.passport.id).first()
        payment = Payment.objects.filter(pk=self.payment.id).first()

        self.assertEqual(booking, self.booking)
        self.assertEqual(passport, self.passport)
        self.assertEqual(payment, self.payment)
