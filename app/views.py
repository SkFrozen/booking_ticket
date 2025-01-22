import time

import stripe
import stripe.error
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from trips.forms import TripSearchForm
from trips.models import Country, Seat, Trip

from .forms import PassportForm, PassportFormSet
from .models import Booking, Passport, Payment
from .tasks import send_ticket_to_user
from .utils import create_checkout_session, generate_seats_map, generate_ticket_pdf


@login_required
def ticket_download_view(request: WSGIRequest, booking_id: int) -> HttpResponse:
    booking = Booking.objects.select_related("passport").get(pk=booking_id)
    if request.user.id == booking.passport.owner.id:
        ticket = generate_ticket_pdf(booking.ticket)
        return FileResponse(
            ticket,
            as_attachment=True,
            filename=f"ticket_{request.user.username}_{booking_id}.pdf",
        )
    return HttpResponseNotFound()


@login_required
def passport_create_view(
    request: WSGIRequest, trip_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Creates new passport for auth user
    Displays form to create new passport for auth user
    """
    if request.method == "POST":
        formset = PassportFormSet(request.POST)
        if formset.is_valid():
            passports = formset.save(commit=False)
            for passport in passports:
                passport.owner = request.user
                passport.save()
            return redirect("passports_list", trip_id)
    else:
        formset = PassportFormSet(queryset=Passport.objects.none())

    context = {
        "formset": formset,
        "trip_id": trip_id,
    }
    return render(request, "app/passport_form.html", context)


@login_required
def passport_update_view(request: WSGIRequest, passport_id: int) -> HttpResponse:
    """
    Updates passport for auth user
    Displays form to update passport for auth user
    """

    passport = Passport.objects.get(pk=passport_id)
    if request.method == "POST":
        form = PassportForm(request.POST, instance=passport)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = PassportForm(instance=passport)
    context = {"form": form}
    return render(request, "app/passport_edit.html", context)


def booking_passports_view(request: WSGIRequest, trip_id: int) -> HttpResponse:
    """
    Displays a list of passports for the auth user
    Or a form to create a new passport for an anonymouse user
    Also generates a seat map for the specified trip
    """

    trip = get_object_or_404(Trip, pk=trip_id)
    seats = trip.seats.all().order_by("id")
    seats_map = generate_seats_map(seats)
    context = {
        "seats_map": seats_map,
        "trip": trip,
    }

    if request.user.is_authenticated:
        passports = Passport.objects.filter(owner=request.user).order_by("id")
        context["passports"] = passports
    else:
        formset = PassportFormSet(queryset=Passport.objects.none())
        context["formset"] = formset

    return render(request, "app/passport_list.html", context)


def booking_seat_view(
    request: WSGIRequest, trip_id: int
) -> HttpResponse | HttpResponseRedirect:
    """
    Recieves a list of booked seats and passports
    Creates a booking for each seat and passport
    Generates information about the booking
    Creates a payment and a checkout session
    Displays a successful page with booking details
    """
    if request.method == "GET":
        seat_ids = request.GET.getlist("seat")
        passports = request.GET.getlist("passport")
        passports = Passport.objects.filter(id__in=passports)

    if request.method == "POST":
        seat_ids = request.POST.getlist("seat")
        formset = PassportFormSet(request.POST)
        passports = []
        for k, form in enumerate(formset):
            number = form.data.get(f"form-{k}-number")
            first_name = form.data.get(f"form-{k}-first_name")
            last_name = form.data.get(f"form-{k}-last_name")
            passport = Passport.objects.filter(
                number=number, first_name=first_name, last_name=last_name
            ).first()

            if passport is None:
                if form.is_valid():
                    passport = form.save()
                else:
                    return HttpResponseBadRequest(
                        "<h1 style='color: red'>Error: Check the entered data</h1>"
                    )
            passports.append(passport)

    if len(seat_ids) != len(passports):
        return HttpResponseBadRequest(
            "<h1 style='color: red'>Error: Incorrect number of seats</h1>"
        )
    domain_url = request.build_absolute_uri("/")[:-1] + "/"
    stripe.api_key = settings.STRIPE_SECRET_KEY
    trip = get_object_or_404(Trip, pk=trip_id)
    seats = Seat.objects.filter(id__in=seat_ids)
    payment = Payment.objects.create()
    seat_passport = dict(zip(seat_ids, passports))
    info_book = {
        "cost": 0,
        "seats": len(seats),
        "trip": trip,
    }
    for seat, passport in seat_passport.items():
        if passport.id is None:
            passport.save()

        seat = seats.get(pk=seat)
        info_book["cost"] += seat.price
        seat.is_booked = True
        seat.save()
        try:
            Booking.objects.create(seat=seat, passport=passport, payment=payment)
        except Exception:
            return redirect("cancelled")

    stripe_session_id = create_checkout_session(stripe, domain_url, seats, payment.id)
    info_book["payment_id"] = payment.id
    info_book["stripe_session_id"] = stripe_session_id
    info_book["time"] = str(int(time.time()))
    return render(request, "app/success-booking.html", {"info_book": info_book})


@csrf_exempt
def payment_view(request: WSGIRequest, stripe_session_id: str) -> HttpResponse:
    """
    Generates a payment link using the Stripe service for the specified payment
    Redirects the user to the payment page
    """
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
        except Exception as e:
            return HttpResponseBadRequest(str(e))

        return redirect(checkout_session.url, code=303)
    return HttpResponseBadRequest(status=400, content="The method is not allowed")


class SuccessPaymentView(TemplateView):
    template_name = "app/success_payment.html"

    def get(self, request: WSGIRequest, payment_id: int) -> HttpResponse:
        payment = Payment.objects.filter(pk=payment_id).first()
        return render(request, self.template_name, {"payment": payment})


class CancelledPaymentView(TemplateView):
    template_name = "app/cancelled_payment.html"


@csrf_exempt
def stripe_webhook(request: WSGIRequest) -> HttpResponse:
    """
    Checks whether the payment was successful and updates the booking status
    Sends a ticket to the user if the payment was successful
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        stripe_session = event.data.object
        assert isinstance(stripe_session, stripe.checkout.Session)

        try:
            payment_id = stripe_session.metadata.get("payment_id")
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            # if Payment does not exist payment will be refunded
            payment_intent = stripe_session.payment_intent
            amount = stripe_session.amount_total
            stripe.Refund.create(payment_intent=payment_intent, amount=amount)
            return HttpResponse(status=200)

        email = stripe_session.customer_details.get("email")
        booking = payment.booking.all()
        payment.paid = True
        payment.save(update_fields=["paid"])
        for book in booking:
            book.status = "paid"
            book.save(update_fields=["status"])

        send_ticket_to_user.delay(payment_id, email)
    elif event["type"] == "checkout.session.expired":
        stripe_session = event.data.object
        assert isinstance(stripe_session, stripe.checkout.Session)

    return HttpResponse(status=200)


@login_required
def reject_booking_view(request: WSGIRequest, booking_id: int) -> HttpResponse:
    """
    Creates a request to cancel a reservation be a registered user
    """

    booking = get_object_or_404(Booking, pk=booking_id)
    booking.seat.is_booked = False
    booking.seat.save()
    booking.delete()
    return redirect("profile")


class DirectionsView(ListView):
    """
    Displays a list of countries on the home page
    """

    model = Country
    template_name = "home.html"
    context_object_name = "countries"

    def get(self, request: WSGIRequest) -> HttpResponse:
        form = TripSearchForm()
        if cache.get("countries"):
            context = {"countries": cache.get("countries"), "search_form": form}

            return render(request, self.template_name, context)
        else:
            countries = Country.objects.all()
            cache.set("countries", countries, 60 * 60)
            context = {"countries": countries, "search_form": form}
            return render(request, self.template_name, context)
