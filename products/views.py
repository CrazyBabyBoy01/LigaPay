from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.


class ProductsView(TemplateView):
    template_name = "products/products.html"
    title = "Услуги"
