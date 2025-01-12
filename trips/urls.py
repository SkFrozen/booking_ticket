from django.urls import path

from .views import cities_list_view, trips_list_by_town_view

urlpatterns = [
    path(
        "direction/<int:country_id>/",
        cities_list_view,
        name="cities_list",
    ),
    path(
        "direction/<int:country_id>/city/<int:city_id>/flights",
        trips_list_by_town_view,
        name="trips_list",
    ),
]
