from email import message
from pyexpat import model

from common.views import ContextMixin
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core import files
from django.shortcuts import HttpResponseRedirect, render
from django.template import context
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
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
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("main:index"))



def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("main:index"))


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
