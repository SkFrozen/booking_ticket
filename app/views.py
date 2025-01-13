import stripe
import stripe.error
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from trips.forms import TripSearchForm
from trips.models import Country, Seat, Trip

from .forms import PassportForm, PassportFormSet
from .models import Booking, Passport, Payment
from .tasks import send_ticket_to_user
from .utils import generate_items_for_payment, generate_seats_map


@csrf_exempt
def stripe_config_view(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


@login_required
def passport_create_view(
    request: WSGIRequest, trip_id: int
) -> HttpResponse | HttpResponseRedirect:
    if request.method == "POST":
        formset = PassportFormSet(request.POST)
        if formset.is_valid():
            passports = formset.save(commit=False)
            for passport in passports:
                passport.owner = request.user
                passport.save()
            return redirect("add_passport", trip_id)
    else:
        formset = PassportFormSet(queryset=Passport.objects.none())

    context = {
        "formset": formset,
        "trip_id": trip_id,
    }
    return render(request, "app/passport_form.html", context)


@login_required
def passport_update_view(request: WSGIRequest, passport_id: int) -> HttpResponse:
    passport = Passport.objects.get(pk=passport_id)
    if request.method == "POST":
        form = PassportForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            Passport.objects.filter(pk=passport_id).update(**cleaned_data)
            return redirect("profile")
    else:
        form = PassportForm(instance=passport)
    context = {"form": form}
    return render(request, "app/passport_edit.html", context)


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
        booking.save()
        bookings.append(booking)
    payment = Payment.objects.create()
    payment.booking.set(bookings)
    info_book["payment"] = payment

    return render(request, "app/success-booking.html", {"info_book": info_book})


@csrf_exempt
def payment_view(request: WSGIRequest, payment_id: int) -> HttpResponse:
    if request.method == "POST":
        domain_url = "http://127.0.0.1:8000/"
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            items = generate_items_for_payment(stripe, payment_id)
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url
                + f"success/{payment_id}"
                + "?session_id={CHECKOUT_SESSION_}",
                cancel_url=domain_url + "cancelled/",
                payment_method_types=["card"],
                metadata={"payment_id": payment_id},
                mode="payment",
                line_items=items,
            )

        except Exception as e:
            return str(e)  # JsonResponse({"error": str(e)})

        return redirect(checkout_session.url, code=303)


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

    print("event type:", event["type"])
    if event["type"] == "checkout.session.completed":
        stripe_session = event.data.object
        assert isinstance(stripe_session, stripe.checkout.Session)

        try:
            payment_id = (
                event.get("data").get("object").get("metadata").get("payment_id")
            )
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            payment_intent = stripe_session.payment_intent
            amount = stripe_session.amount_total
            stripe.Refund.create(payment_intent=payment_intent, amount=amount)
            return HttpResponse(status=200)

        email = event["data"]["object"]["customer_details"]["email"]
        booking = payment.booking.all()
        payment.paid = True
        payment.save(update_fields=["paid"])
        for book in booking:
            book.status = "paid"
            book.save(update_fields=["status"])

        send_ticket_to_user.delay(payment_id, email)

    return HttpResponse(status=200)


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
        form = TripSearchForm()
        if cache.get("countries"):
            print("cache")
            context = {"countries": cache.get("countries"), "search_form": form}

            return render(request, self.template_name, context)
        else:
            print("miss cache")
            countries = Country.objects.all()
            cache.set("countries", countries, 60 * 60)
            context = {"countries": countries, "search_form": form}

            return render(request, self.template_name, context)
