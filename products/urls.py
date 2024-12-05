from django.urls import path

from products.views import ProductsView


app_name = "products"

urlpatterns = [
    path("products/", ProductsView.as_view(), name="products"),
]
