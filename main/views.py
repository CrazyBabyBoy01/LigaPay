from django.http import HttpResponse
from django.shortcuts import render
from django.template import context
from django.views.generic.base import TemplateView


# Create your views here.


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "LigaPay"
        context["subtitle"] = "LigaPay - является гарантом на всех этапах сделки."
        return context
