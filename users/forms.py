from django import forms

from .models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput, label="Password", max_length=128
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        max_length=128,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "date_of_birth",
            "notifications",
        )
        widgets = {
            "date_of_birth": forms.widgets.DateInput(
                attrs={"type": "date"},
            ),
        }

    def clean(self):
        data = self.cleaned_data
        if data["password"] != data["password2"]:
            raise forms.ValidationError("Passwords do not match")
        data.pop("password2")
        return data
