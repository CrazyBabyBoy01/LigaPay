from django.urls import path

from products.views import (
    AccountServiceListView,
    BattlePassServiceListView,
    BoostServiceListView,
    CategoryView,
    DonationServiceListView,
    GeneralServiceListView,
    OtherServiceListView,
    QualificationServiceListView,
    RPServiceListView,
    TrainingServiceListView,
)


app_name = "products"

urlpatterns = [
    path("category/<slug:category_slug>/", CategoryView.as_view(), name="category"),
    path("products/accounts/", AccountServiceListView.as_view(), name="account"),
    path("products/riot-points/", RPServiceListView.as_view(), name="riot-points"),
    path("products/boost/", BoostServiceListView.as_view(), name="boost"),
    path("products/training/", TrainingServiceListView.as_view(), name="training"),
    path("products/battlepass/", BattlePassServiceListView.as_view(), name="battlepass"),
    path("products/donation/", DonationServiceListView.as_view(), name="donation"),
    path("products/services/", GeneralServiceListView.as_view(), name="services"),
    path("products/other/", OtherServiceListView.as_view(), name="other"),
    path("products/qualification/", QualificationServiceListView.as_view(), name="qualification"),
]
