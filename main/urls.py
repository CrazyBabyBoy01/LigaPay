from django.urls import path

from main import views
from main.views import index


app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
]
