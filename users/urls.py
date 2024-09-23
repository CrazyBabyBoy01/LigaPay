from django.urls import path

from users.views import registration

from . import views


app_name = "users"

urlpatterns = [
    path("registration/", views.registration, name="users"),
]
