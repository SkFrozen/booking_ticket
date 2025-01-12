from datetime import datetime, timedelta

import requests
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, Sum
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.base import constant_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from trips.models import Country, Seat, Trip

from .forms import PassportFormSet
from .models import Booking, Passport, Payment
from .tasks import send_ticket_to_user
from .utils import generate_items_for_payment, generate_seats_map


@csrf_exempt
def stripe_config_view(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


def booking_passports_view(request: WSGIRequest, trip_id: int) -> HttpResponse:
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
    if request.method == "GET":
        seat_ids = request.GET.getlist("seat")
        passports = request.GET.getlist("passport")
        if len(seat_ids) != len(passports):
            return HttpResponseBadRequest(
                "<h1 style='color: red'>Error: Incorrect number of seats</h1>"
            )
        passports = Passport.objects.filter(id__in=passports)

    if request.method == "POST":
        seat_ids = request.POST.getlist("seat")
        formset = PassportFormSet(request.POST)
        if formset.is_valid():
            passports = formset.save(commit=False)
            if len(seat_ids) != len(passports):
                return HttpResponseBadRequest(
                    "<h1 style='color: red'>Error: Incorrect number of seats</h1>"
                )
    trip = get_object_or_404(Trip, pk=trip_id)
    seats = Seat.objects.filter(id__in=seat_ids)
    seat_passport = dict(zip(seat_ids, passports))
    info_book = {
        "cost": 0,
        "seats": len(seats),
        "trip": trip,
    }
    bookings = []

    for seat, passport in seat_passport.items():
        if passport.id is None:
            passport.save()

        seat = seats.get(pk=seat)
        info_book["cost"] += seat.price
        seat.is_booked = True
        seat.save()
        booking = Booking(seat=seat, passport=passport)
        bookings.append(booking)

    bookings = Booking.objects.bulk_create(bookings)
    payment = Payment.objects.create()
    payment.booking.set(bookings)
    info_book["payment"] = payment

    return render(request, "app/success-booking.html", {"info_book": info_book})


@csrf_exempt
def payment_view(request: WSGIRequest, payment_id: int) -> HttpResponse:
    if request.user.is_authenticated:
        email = request.user.email
    else:
        email = request.POST.get("email")

    if request.method == "GET":
        domain_url = "http://127.0.0.1:8000/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        items = generate_items_for_payment(stripe, payment_id)
        try:
            print("check: ", 1)
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_}",
                cancel_url=domain_url + "cancelled/",
                payment_method_types=["card"],
                metadata={"payment_id": payment_id},
                mode="payment",
                line_items=items,
            )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


class SuccessView(TemplateView):
    template_name = "app/success_payment.html"


class CancelledView(TemplateView):
    template_name = "app/cancelled_payment.html"


@csrf_exempt
def stripe_webhook(request: WSGIRequest) -> HttpResponse:
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

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        payment_id = event["data"]["object"]["metadata"]["payment_id"]
        payment = Payment.objects.get(pk=payment_id)
        payment.paid = True
        payment.save(update_fields=["paid"])
        booking = payment.booking.all()
        for book in booking:
            book.status = "paid"
            book.save(update_fields=["status"])

    return HttpResponse(status=200)


def cancelled_payment_view(request: WSGIRequest) -> HttpResponse:
    payment_id = request.GET.get("payment_id")
    payment = Payment.objects.get(pk=payment_id)
    payment.paid = False
    payment.save(update_fields=["paid"])
    booking = payment.booking.all()
    for book in booking:
        book.status = "rejected"
        book.save(update_fields=["status"])
    msg = "Please try again"
    return render(request, "app/cancelled_payment.html", {"msg": msg})


@login_required
def reject_booking_view(request: WSGIRequest, booking_id: int) -> HttpResponse:
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.seat.is_booked = False
    booking.seat.save()
    booking.delete()
    return redirect("profile")


class DirectionsView(ListView):
    model = Country
    template_name = "home.html"
    context_object_name = "countries"

    def get(self, request: WSGIRequest) -> HttpResponse:
        if cache.get("countries"):
            print("cache")
            return render(
                request, self.template_name, {"countries": cache.get("countries")}
            )
        else:
            print("miss cache")
            countries = Country.objects.all()
            cache.set("countries", countries, 60 * 60)
            return render(request, self.template_name, {"countries": countries})
