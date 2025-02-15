from django.urls import path

from .views import (
    CancelledPaymentView,
    DirectionsView,
    SuccessPaymentView,
    booking_passports_view,
    booking_seat_view,
    passport_create_view,
    passport_update_view,
    payment_view,
    reject_booking_view,
    stripe_webhook,
    ticket_download_view,
)

urlpatterns = [
    path("", DirectionsView.as_view(), name="directions"),
    path("webhook/", stripe_webhook),
    path("ticket/<int:booking_id>", ticket_download_view, name="download_ticket"),
    path(
        "booking/passport/<int:passport_id>/update/",
        passport_update_view,
        name="passport_update",
    ),
    path(
        "booking/passport/<int:trip_id>/create/",
        passport_create_view,
        name="passport_create",
    ),
    path(
        "booking/passport/<int:trip_id>/",
        booking_passports_view,
        name="passports_list",
    ),
    path(
        "booking/<int:trip_id>/seats/",
        booking_seat_view,
        name="book_seat",
    ),
    path("booking/payment/<str:stripe_session_id>/", payment_view, name="payment"),
    path(
        "success/<int:payment_id>/",
        SuccessPaymentView.as_view(),
        name="success_payment",
    ),
    path("cancelled/", CancelledPaymentView.as_view(), name="cancelled"),
    path("booking/reject/<int:booking_id>", reject_booking_view, name="reject"),
]
