from django.contrib import admin

from .forms import SeatCreateForm, SeatUpdateForm
from .models import Company, Country, Seat, Trip


class HasSeatsFilter(admin.SimpleListFilter):
    """
    Filter by trips with available seats
    """
    title = "trip"
    parameter_name = "trip"

    def lookups(self, request, model_admin):
        qs = (
            Trip.objects.filter(seats__gt=0)
            .distinct()
            .values("id", "town_from", "town_to")
        )
        lookup = ((obj["id"], f"{obj["id"]}: {obj["town_from"]} - {obj["town_to"]}") for obj in qs)
        return lookup

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(trip_id=self.value()).all()
        return queryset


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "town_from",
        "town_to",
        "airport",
        "plane",
        "time_out",
        "time_in",
        "company",
        "country",
    )
    list_filter = ("company", "country", "airport", "town_from")
    list_per_page = 50
    search_fields = ("id", "time_out", "time_in", "plane", "town_to")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "price",
        "is_booked",
        "trip",
    )
    list_filter = ("is_booked", HasSeatsFilter)
    list_per_page = 50
    search_fields = ("number", "price")
    ordering = ("trip",)
    actions = ("mark_as_booked",)

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            amount = form.cleaned_data.pop("amount")
            objs = [Seat(**form.cleaned_data, number=k+1) for k in range(amount)]
            Seat.objects.bulk_create(objs)
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return SeatCreateForm
        return SeatUpdateForm
        

    def get_queryset(self, request):
        seats = Seat.objects.all().select_related("trip")
        return seats
    
    @admin.action(description="mark as booked")
    def mark_as_booked(self, request, queryset):
        queryset.update(is_booked=True)
        self.message_user(request, "Seats marked as booked")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
