from django.core.paginator import Paginator
from django.db.models import Min
from django.shortcuts import render

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
