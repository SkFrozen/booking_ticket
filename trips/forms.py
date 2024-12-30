from django import forms

from .models import Trip


class CreateSeatsForm(forms.Form):
    seats = forms.IntegerField(label="Seats", min_value=1)
    price = forms.IntegerField(label="Price", min_value=1)
    trip = forms.ModelChoiceField(queryset=Trip.objects.all(), label="Trip")
