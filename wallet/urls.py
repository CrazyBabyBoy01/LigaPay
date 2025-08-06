from django.urls import path

from wallet.views import DepositView


app_name = 'wallet'

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='wallet_deposit'),
]
