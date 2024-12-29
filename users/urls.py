from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import profile_view, register_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
]
