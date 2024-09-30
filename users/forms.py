from logging import PlaceHolder
from pyexpat import model

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "header__input", "placeholder": "Введите Ваш Логин"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "header__input", "placeholder": "Введите Ваш Пароль"})
    )

    class Meta:
        model = User
        fields = ("username", "password")


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "header__input", "placeholder": "Введите Логин"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "header__input", "placeholder": "Введите Пароль"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "header__input", "placeholder": "Подтвердите Пароль"})
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={"class": "header__input", "placeholder": "Введите Почту"})
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")
