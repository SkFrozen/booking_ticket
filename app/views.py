from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from trips.models import Country, Seat, Trip

from .models import Booking, Payment


@login_required
def booking_seats_chart_view(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    seats = trip.seats.all().order_by("id")
    return render(request, "app/book-trip.html", {"seats": seats, "trip": trip})


@login_required
def booking_seat_view(request, trip_id):
    seat_ids = request.GET.getlist("seat")
    if seat_ids is not None:
        seats = Seat.objects.filter(id__in=seat_ids)
        info_book = {
            "total_price": 0,
            "total_seats": len(seats),
            "trip_id": trip_id,
        }
        for seat in seats:
            info_book["total_price"] += seat.price
            seat.is_booked = True
            seat.save()
            Booking.objects.create(seat=seat, user=request.user, trip_id=trip_id)

        return render(request, "app/success-booking.html", {"info_book": info_book})

    return redirect("booking", trip_id=trip_id)


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    try:
        payment = Payment.objects.create(booking_id=booking.id, user_id=request.user.id)
        booking.paid = True
        booking.save()
        msg = "Thank you for your payment. We send your ticket in your email"
        return render(request, "app/success-booking.html", {"msg": msg})
    except Exception as e:
        msg = "Error: " + str(e) + ". Please try again"
        return render(request, "app/success-booking.html", {"msg": msg})


@login_required
def reject_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.seat.is_booked = False
    booking.seat.save()
    booking.delete()
    return redirect("profile")


class DirectionsView(ListView):
    model = Country
    template_name = "home.html"
    context_object_name = "countries"

    def get(self, request):
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
