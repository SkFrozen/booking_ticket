from django.urls import path

from .views import (
    DirectionsView,
    booking_seat_view,
    booking_seats_chart_view,
    payment_view,
    reject_booking_view,
)

urlpatterns = [
    path("", DirectionsView.as_view(), name="directions"),
    path("booking/<int:trip_id>/", booking_seats_chart_view, name="booking"),
    path(
        "booking/<int:trip_id>/seats/",
        booking_seat_view,
        name="book_seat",
    ),
    path("booking/payment/<int:booking_id>", payment_view, name="payment"),
    path("booking/reject/<int:booking_id>", reject_booking_view, name="reject"),
]
