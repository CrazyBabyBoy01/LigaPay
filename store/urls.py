from django.urls import path

from .views import StoreSkinsView


app_name = 'store'

urlpatterns = [
    path('skins/', StoreSkinsView.as_view(), name='store_skins'),
]
