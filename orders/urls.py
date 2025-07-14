from django.urls import path

from .views import CancelOrderView, ConfirmOrderView, CreateOrderView, OrderListView, SaleListView


app_name = "orders"

urlpatterns = [
    path("buy/<str:model_name>/<int:product_id>/", CreateOrderView.as_view(), name="create_order"),
    path("my-orders/", OrderListView.as_view(), name="my_orders"),
    path("confirm/<int:order_id>/", ConfirmOrderView.as_view(), name="confirm_order"),
    path("cancel/<int:order_id>/", CancelOrderView.as_view(), name="cancel_order"),
    path("sales/", SaleListView.as_view(), name="my_sales"),
]
