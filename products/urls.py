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
    RPServiceDetailView,
    RPServiceListView,
    TrainingServiceListView,
)


app_name = "products"

urlpatterns = [
    path("category/<slug:category_slug>/", CategoryView.as_view(), name="category"),
    path("accounts/", AccountServiceListView.as_view(), name="account"),
    path("riot-points/", RPServiceListView.as_view(), name="riot-points"),
    path("riot-points/<int:pk>/", RPServiceDetailView.as_view(), name="riot-points_detail"),
    path("boost/", BoostServiceListView.as_view(), name="boost"),
    path("training/", TrainingServiceListView.as_view(), name="training"),
    path("battlepass/", BattlePassServiceListView.as_view(), name="battlepass"),
    path("donation/", DonationServiceListView.as_view(), name="donation"),
    path("services/", GeneralServiceListView.as_view(), name="services"),
    path("other/", OtherServiceListView.as_view(), name="other"),
    path("qualification/", QualificationServiceListView.as_view(), name="qualification"),
]
