from email.policy import default

from django import forms
from django.utils import timezone

from .models import Passport


class PassportForm(forms.ModelForm):
    class Meta:
        model = Passport
        fields = [
            "number",
            "nationality",
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
        ]
        widgets = {
            "date_of_birth": forms.widgets.SelectDateWidget(
                years=range(1950, timezone.now().year)
            ),
        }


PassportFormSet = forms.modelformset_factory(
    Passport, form=PassportForm, extra=1, can_delete=True
)
