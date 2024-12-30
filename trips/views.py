from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Min
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView

from .forms import CreateSeatsForm
from .models import Trip


def trip_list_by_direction_view(request, direction):
    trips = (
        Trip.objects.filter(country__id=direction)
        .distinct("town_to")
        .order_by("town_to")
    )

    paginator = Paginator(trips, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "trips/trip-list.html", {"page_obj": page_obj})


def trip_list_by_town_view(request, town_to):
    trips = (
        Trip.objects.prefetch_related("seats")
        .filter(town_to=town_to)
        .annotate(min_price=Min("seats__price"))
        .order_by("min_price")
    )

    paginator = Paginator(trips, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "trips/trip-list.html", {"page_obj": page_obj})


class CreateSeatsView(PermissionRequiredMixin, FormView):
    """
    View for creating seats by the admin
    """

    template_name = "trips/create-seats.html"
    form_class = CreateSeatsForm
    permission_required = ["user.is_superuser"]

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            count = form.cleaned_data["seats"]
            price = form.cleaned_data["price"]
            trip = form.cleaned_data["trip"]

            if trip.seats.exists():
                return HttpResponse("Already have seats")

            trip.create_seats(count, price)
            return redirect("create_seats")
        else:
            return render(request, self.template_name, {"form": form})
