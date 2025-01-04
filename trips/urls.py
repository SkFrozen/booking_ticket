from django.urls import path

from .views import trip_list_by_direction_view, trip_list_by_town_view

urlpatterns = [
    path(
        "direction/<int:direction>/",
        trip_list_by_direction_view,
        name="trip_list_by_direction",
    ),
    path(
        "direction/<int:direction>/town/<str:town_to>/",
        trip_list_by_town_view,
        name="detail_trip",
    ),
]
