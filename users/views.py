from django.shortcuts import redirect, render

from users.models import User

from .forms import UserForm


def register_view(request):
    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(cleaned_data)
            user = User.objects.create_user(**cleaned_data)
            return redirect("login")

    return render(request, "registration/register-form.html", {"form": form})


def profile_view(request):
    return render(request, "registration/profile.html")
