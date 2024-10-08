from common.views import ContextMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.template import context
from django.views.generic.base import TemplateView


# Create your views here.


class IndexView(ContextMixin, TemplateView):
    template_name = "main/index.html"
    title = "LigaPay"
    subtitle = "LigaPay - является гарантом на всех этапах сделки."
