from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
)
from django.db import transaction

from users.models import User
from users.tasks import send_email_verification, send_reset_email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'header__input', 'placeholder': 'Введите Ваш Логин'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'header__input', 'placeholder': 'Введите Ваш Пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'header__input', 'placeholder': 'Введите Логин'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'header__input', 'placeholder': 'Введите Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'header__input', 'placeholder': 'Подтвердите Пароль'})
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'header__input', 'placeholder': 'Введите Почту'})
    )
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'captcha')

    def save(self, commit=True):
        user = super().save(commit=True)
        send_email_verification.delay(user.id)
        return user


class UserProfileForm(UserChangeForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-group__input', 'readonly': True})
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'input-group__input', 'readonly': True})
    )
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-group__input'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-group__input'}))
    image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'input-group__input'}), required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'image')


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.CharField(label='Логин или Email', max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']

        user = None

        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
        elif User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        if user is None:
            raise forms.ValidationError('Пользователь с таким логином или email не найден.')
        return user.email

    def save(self, *args, **kwargs):
        """
        Переопределённый метод save для кастомной логики отправки письма.
        """
        user_email = self.cleaned_data['email']
        # Вызываем отправку email через Celery или другую логику
        transaction.on_commit(lambda: send_reset_email.delay(user_email))
        super().save(*args, **kwargs)  # Не забываем вызвать оригинальный метод
        # Отправка письма через Celery


class EmailChangeForm(forms.ModelForm):
    new_email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['new_email']

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError('Этот адрес электронной почты уже занят.')
        return new_email
