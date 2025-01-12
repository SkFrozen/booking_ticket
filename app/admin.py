from django.contrib import admin

from .models import Booking, Passport, Payment


@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "number",
        "nationality",
        "first_name",
        "last_name",
        "date_of_birth",
        "sex",
    )
    list_filter = ("nationality", "sex")
    search_fields = ("id", "owner__username", "date_of_birth")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "seat",
        "status",
        "passport",
        "created_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("id", "passport__first_name", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "paid", "created_at")
    list_filter = ("paid",)
    search_fields = ("id", "created_at")
