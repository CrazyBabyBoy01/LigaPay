from django.urls import path

from users.views import autorization, logout, profile, registration

from . import views


app_name = "users"

urlpatterns = [
    path("registration/", views.registration, name="registration"),
    path("autorization/", views.autorization, name="autorization"),
    path("profile/", views.profile, name="profile"),
    path("logout/", logout, name="logout"),
]
