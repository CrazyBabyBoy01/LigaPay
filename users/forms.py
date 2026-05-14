from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string

from users.models import User
from users.orchestrators import send_verification_email


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации пользователя.
    Переопределяет стандартные поля для стилизации под шаблон.
    """

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
    """
    Форма регистрации нового пользователя.
    Включает капчу и вызывает задачу на отправку письма с подтверждением.
    """

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
        send_verification_email(user.id)
        return user


class UserProfileForm(UserChangeForm):
    """
    Форма редактирования профиля.
    Логин и почта доступны только для чтения, редактируются только остальные данные.
    """

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
    """
    Кастомная форма сброса пароля.
    Позволяет искать пользователя как по email, так и по логину.
    """

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

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = 'Сброс пароля на LigaPay'
        message = render_to_string(email_template_name, context)

        django_send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )


class EmailChangeForm(forms.ModelForm):
    """
    Форма для смены email.
    Проверяет уникальность нового адреса.
    """

    new_email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['new_email']

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError('Этот адрес электронной почты уже занят.')
        return new_email
