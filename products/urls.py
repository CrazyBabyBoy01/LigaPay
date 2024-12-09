from django.urls import path

from products.views import CategoryDescriptionView, ProductsView


app_name = "products"

urlpatterns = [
    path("category-description/<slug:category_slug>/", CategoryDescriptionView.as_view(), name="category_description"),
    path("products/<slug:category_slug>/", ProductsView.as_view(), name="products_detail"),
    path("", ProductsView.as_view(), name="products"),
]
