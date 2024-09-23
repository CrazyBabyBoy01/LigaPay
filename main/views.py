from django.http import HttpResponse
from django.shortcuts import render
from django.template import context


# Create your views here.


def index(request):
    context = {"title": "LigaPay", "subtitle": "LigaPay - является гарантом на всех этапах сделки."}
    return render(request, "main/index.html", context)


def about(request):
    return HttpResponse("About page")
