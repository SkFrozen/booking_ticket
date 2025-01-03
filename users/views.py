from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from app.models import Booking

from .forms import UserForm
from .models import User
from .tasks import delete_user_task, send_register_email_task


def register_view(request):
    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = User.objects.create_user(**cleaned_data, is_active=False)
            domain = str(get_current_site(request))

            msg: bool = send_register_email_task.delay(domain, user.id)
            # send_register_email_task.apply_async(args=[domain, user.id])
            delete_user_task.apply_async(args=[user.id], countdown=30)
            return render(
                request,
                "registration/login.html",
                {"form": AuthenticationForm, "msg": msg},
            )

    return render(request, "registration/register-form.html", {"form": form})


def confirm_register_view(request, uidb64, token):
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
def profile_view(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("seat")
        .select_related("trip")
    )
    return render(request, "registration/profile.html", {"bookings": bookings})
