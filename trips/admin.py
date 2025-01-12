from django.contrib import admin

from .models import Airport, City, Company, Country, Plane, Seat, Trip


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
            .values("id", "departure_airport", "arrival_airport")
        )
        lookup = ((obj["id"], f"{obj["id"]}: {obj["departure_airport"]} - {obj["arrival_airport"]}") for obj in qs)
        return lookup

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(trip_id=self.value()).all()
        return queryset


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "departure_airport",
        "arrival_airport",
        "plane",
        "time_out",
        "time_in",
        "company",
    )
    list_filter = ("company", "departure_airport")
    list_per_page = 50
    search_fields = ("id", "time_out", "time_in", "plane")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "price",
        "is_booked",
        "trip",
        "seat_class"
    )
    list_filter = ("is_booked", HasSeatsFilter, "seat_class")
    list_per_page = 50
    search_fields = ("number", "price", "trip")
    ordering = ("trip",)
    actions = ("mark_as_booked",)
    

    def get_queryset(self, request):
        seats = Seat.objects.all().select_related("trip")
        return seats
    
    @admin.action(description="mark as booked")
    def mark_as_booked(self, request, queryset):
        queryset.update(is_booked=True)
        self.message_user(request, "Seats marked as booked")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name",)
    list_filter = ("country",)

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city")
    search_fields = ("name", "city")



@admin.register(Plane)
class PlaneAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "seat_configuration", "business_class_price", "economy_class_price")
    search_fields = ("model",)
    
