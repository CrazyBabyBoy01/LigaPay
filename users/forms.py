import uuid
from datetime import timedelta
from logging import PlaceHolder
from pyexpat import model

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserChangeForm, UserCreationForm
from django.template.defaultfilters import first
from django.utils.timezone import now

from users.models import EmailVerification, User


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
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "header__input", "placeholder": "Введите Логин"}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "header__input", "placeholder": "Введите Пароль"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "header__input", "placeholder": "Подтвердите Пароль"})
    )
    email = forms.CharField(widget=forms.EmailInput(attrs={"class": "header__input", "placeholder": "Введите Почту"}))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "captcha")

    def save(self, commit=True):
        user = super().save(commit=True)
        expiration = now() + timedelta(hours=48)
        record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
        record.send_verification_email()
        return user


class UserProfileForm(UserChangeForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input-group__input", "readonly": True}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"class": "input-group__input", "readonly": True}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "input-group__input"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "input-group__input"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "input-group__input"}), required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "image")


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.CharField(label="Логин или Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data["email"]

        user = None

        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
        elif User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        if user is None:
            raise forms.ValidationError("Пользователь с таким логином или email не найден.")
        return user.email


class EmailChangeForm(forms.ModelForm):
    new_email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["new_email"]

    def clean_new_email(self):
        new_email = self.cleaned_data.get("new_email")
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("Этот адрес электронной почты уже занят.")
        return new_email
