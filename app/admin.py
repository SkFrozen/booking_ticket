from django.contrib import admin

from .models import Booking, Payment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "paid",
        "seat",
        "user",
        "created_at",
        "updated_at",
    )
    list_filter = ("paid",)
    search_fields = ("id", "user__username", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("id", "user__username", "created_at")
