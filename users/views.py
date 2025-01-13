from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from app.models import Booking, Passport

from .forms import UserForm
from .models import User
from .tasks import delete_user_task, send_register_email_task


def register_view(request: WSGIRequest) -> HttpResponse:
    """
    View function for user registration.
    Sends confirmation email to the user
    Deletes the user if he has not confirmed the registration
    """

    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = User.objects.create_user(**cleaned_data, is_active=False)
            domain = str(get_current_site(request))

            msg: bool = send_register_email_task.apply_async(args=[domain, user.id])
            delete_user_task.apply_async(args=[user.id], countdown=60)
            return render(
                request,
                "registration/login.html",
                {"form": AuthenticationForm, "msg": msg},
            )

    return render(request, "registration/register-form.html", {"form": form})


def confirm_register_view(
    request: WSGIRequest, uidb64: str, token: str
) -> HttpResponseRedirect | HttpResponse | None:
    username = force_str(urlsafe_base64_decode(uidb64))
    try:
        user = User.objects.get(username=username)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])

            return redirect("login")
    except User.DoesNotExist:
        return render(
            request,
            "registration/invalid_email_confirm.html",
            {"username": username},
        )


@login_required
def profile_view(request: WSGIRequest) -> HttpResponse:
    """
    View function for user profile page.
    Collects information about the user's bookings and passports
    """
    user = request.user
    passports = Passport.objects.filter(owner=user).all()
    bookings = (
        Booking.objects.filter(passport__owner=user)
        .select_related(
            "passport",
            "seat",
            "seat__trip",
            "seat__trip__departure_airport",
            "seat__trip__arrival_airport",
            "seat__trip__departure_airport__city",
            "seat__trip__arrival_airport__city",
        )
        .prefetch_related("payment")
    )

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    booked_seats_info = []
    for booking in page_obj:
        seat = booking.seat
        trip = seat.trip
        passport = booking.passport
        booked_seats_info.append(
            {
                "trip_number": trip.number,
                "departure_city": trip.departure_airport.city.name,
                "departure_airport": trip.departure_airport.name,
                "arrival_city": trip.arrival_airport.city.name,
                "arrival_airport": trip.arrival_airport.name,
                "time_out": trip.time_out,
                "time_in": trip.time_in,
                "first_name": passport.first_name,
                "last_name": passport.last_name,
                "seat_number": seat.number,
                "price": seat.price,
                "status": booking.status,
                "id": booking.id,
                "payment_id": booking.payment.get().id,
            }
        )
    context = {
        "page_obj": page_obj,
        "bookings": booked_seats_info,
        "passports": passports,
    }
    return render(request, "registration/profile.html", context)
