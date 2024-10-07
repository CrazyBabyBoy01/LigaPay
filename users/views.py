from email import message
from pyexpat import model

from django.contrib import auth
from django.contrib.auth.views import LoginView
from django.core import files
from django.shortcuts import HttpResponseRedirect, render
from django.template import context
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import User


# Create your views here.


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/authorization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Авторизация"
        return context


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("main:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        return context


class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"

    def get_success_url(self):
        return reverse_lazy("users:profile", args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Профиль"
        context["background_image"] = "/static/deps/images/287bff71fe2c1293dbd1be864fb6537f.jpg"
        return context


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
