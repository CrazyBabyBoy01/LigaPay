from django.http import HttpResponse
from django.shortcuts import render
from django.template import context


# Create your views here.
def index(request):
    return render(request, "index.html")


def registration(request):
    context = {"title": "Home", "content": "Главная страница"}
    return render(request, "users/registration.html", context)
