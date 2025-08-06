from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path

from users.views import (
    ChangeEmailView,
    ConfirmEmailChangeView,
    CustomPasswordResetView,
    EmailResetCompleteView,
    EmailResetDoneView,
    EmailVerificationView,
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
    logout,
)


app_name = 'users'

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('autorization/', UserLoginView.as_view(), name='autorization'),
    path('profile/<int:pk>/', login_required(UserProfileView.as_view()), name='profile'),
    path('logout/', logout, name='logout'),
    path(
        'verify/<str:email>/<uuid:code>/',
        EmailVerificationView.as_view(),
        name='email_verification',
    ),
    path('email-reset/', ChangeEmailView.as_view(), name='email_reset'),
    path(
        'confirm-email-change/<uidb64>/<token>/<new_email>/',
        ConfirmEmailChangeView.as_view(),
        name='confirm_email_change',
    ),
    path(
        'password-reset/',
        CustomPasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        'password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path(
        'email-reset-complete/',
        EmailResetCompleteView.as_view(),
        name='email_reset_complete',
    ),
    path(
        'email-reset-done/',
        EmailResetDoneView.as_view(),
        name='email_reset_done',
    ),
]
