from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Min
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Trip


def trip_list_by_direction_view(request: WSGIRequest, direction) -> HttpResponse:
    trips = (
        Trip.objects.filter(country__id=direction)
        .distinct("town_to")
        .order_by("town_to")
    )

    paginator = Paginator(trips, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(
        request, "trips/trip-list.html", {"page_obj": page_obj, "direction": direction}
    )


def trip_list_by_town_view(
    request: WSGIRequest, direction: int, town_to: str
) -> HttpResponse:
    date_now = timezone.now()
    date_out = timezone.make_aware(
        datetime(date_now.year, date_now.month, date_now.day)
    ) + timedelta(days=1)
    trips = (
        Trip.objects.prefetch_related("seats")
        .filter(town_to=town_to, time_out__gt=date_out)
        .annotate(min_price=Min("seats__price"))
        .order_by("min_price")
    )

    paginator = Paginator(trips, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request, "trips/trip-list.html", {"page_obj": page_obj, "direction": direction}
    )
