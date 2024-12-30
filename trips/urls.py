from django.urls import path

from .views import CreateSeatsView, trip_list_by_direction_view, trip_list_by_town_view

urlpatterns = [
    path(
        "direction/<int:direction>/",
        trip_list_by_direction_view,
        name="trips_list_by_direction",
    ),
    path("town/<str:town_to>/", trip_list_by_town_view, name="detail_trip"),
    path("create_seats/", CreateSeatsView.as_view(), name="create_seats"),
]
