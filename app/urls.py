from django.urls import path

from .views import (
    CancelledView,
    DirectionsView,
    SuccessView,
    booking_passports_view,
    booking_seat_view,
    cancelled_payment_view,
    payment_view,
    reject_booking_view,
    stripe_config_view,
    stripe_webhook,
)

urlpatterns = [
    path("", DirectionsView.as_view(), name="directions"),
    path("config/", stripe_config_view, name="config"),
    path(
        "booking/passport/<int:trip_id>/",
        booking_passports_view,
        name="add_passport",
    ),
    path(
        "booking/<int:trip_id>/seats/",
        booking_seat_view,
        name="book_seat",
    ),
    path("booking/payment/<int:payment_id>", payment_view, name="payment"),
    path("success/", SuccessView.as_view(), name="success"),
    path("cancelled/", CancelledView.as_view(), name="cancelled"),
    path("booking/reject/<int:booking_id>", reject_booking_view, name="reject"),
    path("webhook/", stripe_webhook),
]
