from email import message

from django.contrib import auth
from django.core import files
from django.shortcuts import HttpResponseRedirect, render
from django.template import context
from django.urls import reverse

from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import User


# Create your views here.


def autorization(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse("index"))
    else:
        form = UserLoginForm()
    context = {"title": "Авторизация", "content": "Главная страница", "form": form}
    return render(request, "users/authorization.html", context)


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserRegistrationForm()
    context = {"title": "Регистрация", "content": "Регистрация", "form": form}
    return render(request, "users/registration.html", context)


def profile(request):
    if request.method == "POST":
        form = UserProfileForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("users:profile"))
    else:
        form = UserProfileForm(instance=request.user)
    context = {
        "title": "Профиль",
        "content": "Профиль",
        "background_image": "/static/deps/images/287bff71fe2c1293dbd1be864fb6537f.jpg",
        "form": form,
    }
    return render(request, "users/profile.html", context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("index"))
