from urllib import request

from django import forms
from django.forms.widgets import TextInput

from .models import Seat, Trip


class SeatCreateForm(forms.ModelForm):
    amount = forms.IntegerField(label="Amount", min_value=1)

    class Meta:
        model = Seat
        fields = ("amount", "price", "trip")


class SeatUpdateForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = ("number", "price", "trip", "is_booked")


class TripSearchForm(forms.ModelForm):
    departure_city = forms.CharField(
        required=False,
        widget=TextInput(attrs={"placeholder": "Departure city"}),
        label="",
    )
    arrival_city = forms.CharField(
        required=False,
        widget=TextInput(attrs={"placeholder": "Arrival city"}),
        label="",
    )
    time_out = forms.DateTimeField(
        required=False,
        label="",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Trip
        fields = ("departure_city", "arrival_city", "time_out")

    def clean(self):
        cleaned_data = super().clean()
        departure_city = cleaned_data.get("departure_city")
        arrival_city = cleaned_data.get("arrival_city")
        time_out = cleaned_data.get("time_out")

        if not (departure_city or arrival_city or time_out):
            raise forms.ValidationError("You must specify at least one field")
        return cleaned_data
