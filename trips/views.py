from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import City, Trip


def cities_list_view(request: WSGIRequest, country_id: int) -> HttpResponse:
    cities = (
        City.objects.filter(country__id=country_id)
        .select_related("country")
        .order_by("name")
    )
    paginator = Paginator(cities, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "trips/cities_list.html", {"page_obj": page_obj})


def trips_list_by_town_view(
    request: WSGIRequest, country_id: int, city_id: int
) -> HttpResponse:
    date_now = timezone.now()
    date_out = timezone.make_aware(
        datetime(date_now.year, date_now.month, date_now.day)
    ) + timedelta(days=1)

    trips = (
        Trip.objects.filter(arrival_airport__city=city_id, time_out__gt=date_out)
        .select_related(
            "arrival_airport__city",
            "departure_airport__city",
            "plane",
            "company",
        )
        .order_by("-time_out")
    )

    paginator = Paginator(trips, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {"page_obj": page_obj, "country_id": country_id}

    return render(
        request,
        "trips/trip-list.html",
        context,
    )
