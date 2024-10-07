from django.contrib.auth.decorators import login_required
from django.urls import path

from users.views import UserLoginView, UserProfileView, UserRegistrationView, logout

from . import views


app_name = "users"

urlpatterns = [
    path("registration/", UserRegistrationView.as_view(), name="registration"),
    path("autorization/", UserLoginView.as_view(), name="autorization"),
    path("profile/<int:pk>/", login_required(UserProfileView.as_view()), name="profile"),
    path("logout/", logout, name="logout"),
]
