from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from trips.forms import TripSearchForm

from .models import City, Trip


def cities_list_view(request: WSGIRequest, country_id: int) -> HttpResponse:
    """
    Cities list view
    Returns a list of cities in the specified country using country_id
    """
    form = TripSearchForm()
    cities = (
        City.objects.filter(country__id=country_id)
        .select_related("country")
        .order_by("name")
    )
    paginator = Paginator(cities, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {"page_obj": page_obj, "search_form": form}

    return render(request, "trips/cities_list.html", context)


def trips_list_by_town_view(
    request: WSGIRequest, country_id: int, city_id: int
) -> HttpResponse:
    """
    Returns a list of trips to the specified city using city_id,
    filtered by date
    """
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


def trips_search_list_view(request: WSGIRequest) -> HttpResponse:
    """
    Returns a list of trips based on the city of departure or arrival
    or the time of departure
    """

    form = TripSearchForm(request.GET)
    if form.is_valid():
        departure_city = form.cleaned_data.get("departure_city", "")
        arrival_city = form.cleaned_data.get("arrival_city", "")
        time_out = form.cleaned_data.get("time_out", "")

        if not time_out:
            time_out = timezone.now()

        trips = (
            Trip.objects.filter(
                departure_airport__city__name__icontains=departure_city,
                arrival_airport__city__name__icontains=arrival_city,
                time_out__gte=time_out,
            )
            .select_related(
                "arrival_airport__city",
                "departure_airport__city",
                "plane",
                "company",
            )
            .order_by("-time_out")
        )
        context = {"page_obj": trips}
        return render(request, "trips/trip-list.html", context)
    else:
        return redirect("directions")
