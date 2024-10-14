from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from users.views import EmailVerificationView, UserLoginView, UserProfileView, UserRegistrationView, logout

from . import views


app_name = "users"

urlpatterns = [
    path("registration/", UserRegistrationView.as_view(), name="registration"),
    path("autorization/", UserLoginView.as_view(), name="autorization"),
    path("profile/<int:pk>/", login_required(UserProfileView.as_view()), name="profile"),
    path("logout/", logout, name="logout"),
    path("verify/<str:email>/<uuid:code>/", EmailVerificationView.as_view(), name="email_verification"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
