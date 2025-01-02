from django import forms

from .models import Seat


class SeatCreateForm(forms.ModelForm):
    amount = forms.IntegerField(label="Amount", min_value=1)

    class Meta:
        model = Seat
        fields = ("amount", "price", "trip")


class SeatUpdateForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = ("number", "price", "trip", "is_booked")
