import uuid
from email import message
from pyexpat import model

from common.views import ContextMixin
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core import files
from django.core.mail import send_mail
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.template import context
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from users.forms import CustomPasswordResetForm, EmailChangeForm, UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import EmailVerification, User


# Create your views here.


class UserLoginView(ContextMixin, LoginView):
    form_class = UserLoginForm
    template_name = "users/authorization.html"
    title = "Авторизация"
    # authentication_form = AuthenticationForm

    def form_valid(self, form):
        # Если "Запомнить меня" не установлен, установить сессию как сессионную
        remember_me = self.request.POST.get("remember_me")  # Получаем значение чекбокса

        if not remember_me:
            # Сессия завершится, когда пользователь закроет браузер
            self.request.session.set_expiry(0)
        else:
            # Устанавливаем срок действия сессии, например, на 2 недели
            self.request.session.set_expiry(1209600)  # 2 недели в секундах

        return super().form_valid(form)


class UserRegistrationView(SuccessMessageMixin, ContextMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:autorization")
    success_message = "Вы успешно зарегистрированы! На вашу почту отправлено письмо с подтверждением."
    title = "Регистрация"


class UserProfileView(ContextMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    title = "Профиль"
    background_image = "/static/deps/images/287bff71fe2c1293dbd1be864fb6537f.jpg"

    def get_success_url(self):
        return reverse_lazy("users:profile", args=(self.object.id,))


class EmailVerificationView(ContextMixin, TemplateView):
    title = "Подтверждение электронной почты"
    template_name = "users/email_verification.html"
    background_image = "/static/deps/images/SB_Riven.jpg"

    def get(self, request, *args, **kwargs):
        code = kwargs["code"]
        user = User.objects.get(email=kwargs["email"])
        if not user.is_verified_email:
            email_verifications = EmailVerification.objects.filter(user=user, code=code)
            if email_verifications.exists() and not email_verifications.first().is_expired():
                user.is_verified_email = True
                user.save()
                return super().get(request, *args, **kwargs)

        # Проверка на смену почты
        if user.email_change_token == code and user.new_email:
            # Обновляем email пользователя
            user.email = user.new_email
            user.save()

            # Сбрасываем временные данные
            user.new_email = None
            user.email_change_token = None
            user.save()

            return super().get(request, *args, **kwargs)

        # Перенаправление, если код неверный или истек
        return HttpResponseRedirect(reverse("main:index"))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("main:index"))


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "users/password_reset.html"  # Используйте ваш шаблон
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")


class ChangeEmailView(FormView):
    template_name = "users/email_reset.html"
    form_class = EmailChangeForm

    def form_valid(self, form):
        new_email = form.cleaned_data["new_email"]
        user = self.request.user

        # Генерируем ссылку подтверждения
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        confirm_url = self.request.build_absolute_uri(
            reverse("users:confirm_email_change", kwargs={"uidb64": uid, "token": token, "new_email": new_email})
        )

        # Отправляем письмо на старый email
        send_mail(
            "Подтверждение смены электронной почты",
            f"Перейдите по ссылке, чтобы подтвердить изменение email: {confirm_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        messages.success(self.request, "Ссылка для подтверждения отправлена на ваш старый email.")
        return redirect("users:email_reset_done")  # перенаправление после успешного запроса на изменение


class EmailResetCompleteView(TemplateView):
    template_name = "users/email_reset_complete.html"
    title = ("Email reset complete")

class EmailResetDoneView(TemplateView):
    template_name = "users/email_reset_done.html"
    title = ("Email reset done")


class ConfirmEmailChangeView(View):
    def get(self, request, uidb64, token, new_email):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email = new_email
            user.save()
            messages.success(request, "Ваш email успешно изменен!")
            return redirect("users:email_reset_complete")  # перенаправление после подтверждения
        messages.error(request, "Ссылка для подтверждения недействительна.")
        return redirect("users:email_reset_complete")


# def autorization(request):
#     if request.method == "POST":
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST["username"]
#             password = request.POST["password"]
#             user = auth.authenticate(username=username, password=password)
#             if user:
#                 auth.login(request, user)
#                 return HttpResponseRedirect(reverse("main:index"))
#     else:
#         form = UserLoginForm()
#     context = {"title": "Авторизация", "content": "Главная страница", "form": form}
#     return render(request, "users/authorization.html", context)

# def registration(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse("main:index"))
#     else:
#         form = UserRegistrationForm()
#     context = {"title": "Регистрация", "content": "Регистрация", "form": form}
#     return render(request, "users/registration.html", context)


# def profile(request):
#     if request.method == "POST":
#         form = UserProfileForm(instance=request.user, data=request.POST, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse("users:profile"))
#     else:
#         form = UserProfileForm(instance=request.user)
#     context = {
#         "title": "Профиль",
#         "content": "Профиль",
#         "background_image": "/static/deps/images/287bff71fe2c1293dbd1be864fb6537f.jpg",
#         "form": form,
#     }
#     return render(request, "users/profile.html", context)
