from django.contrib import auth
from django.shortcuts import HttpResponseRedirect, render
from django.template import context
from django.urls import reverse

from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User


# Create your views here.


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserRegistrationForm()
    context = {"title": "Home", "content": "Главная страница", "form": form}
    return render(request, "users/registration.html", context)


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
    context = {"title": "Home", "content": "Главная страница", "form": form}
    return render(request, "users/authorization.html", context)
