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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
