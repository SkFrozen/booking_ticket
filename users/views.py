from django.shortcuts import redirect, render

from app.models import Booking
from users.models import User

from .forms import UserForm


def register_view(request):
    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = User.objects.create_user(**cleaned_data)
            return redirect("login")

    return render(request, "registration/register-form.html", {"form": form})


def profile_view(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("seat")
        .select_related("trip")
    )
    return render(request, "registration/profile.html", {"bookings": bookings})
