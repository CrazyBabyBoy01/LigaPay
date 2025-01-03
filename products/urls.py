from django.urls import path

from products.views import (
    AccountServiceListView,
    BattlePassServiceListView,
    BoostServiceListView,
    CategoryView,
    DonationServiceListView,
    RPServiceListView,
    TrainingServiceListView,
    GeneralServiceListView,
    OtherServiceListView,
    QualificationServiceListView,
)


app_name = "products"

urlpatterns = [
    path("category/<slug:category_slug>/", CategoryView.as_view(), name="category"),
    path("account/<slug:slug>/", AccountServiceListView.as_view(), name="account"),
    path("riot-points/<slug:slug>/", RPServiceListView.as_view(), name="riot-points"),
    path("boost/<slug:slug>/", BoostServiceListView.as_view(), name="boost"),
    path("training/<slug:slug>/", TrainingServiceListView.as_view(), name="training"),
    path("battlepass/<slug:slug>/", BattlePassServiceListView.as_view(), name="battlepass"),
    path("donation/<slug:slug>/", DonationServiceListView.as_view(), name="donation"),
    path("services/<slug:slug>/", GeneralServiceListView.as_view(), name="services"),
    path("other/<slug:slug>/", OtherServiceListView.as_view(), name="other"),
    path("qualification/<slug:slug>/", QualificationServiceListView.as_view(), name="qualification"),
    # path("products/<slug:category_slug>/", ProductsView.as_view(), name="products_detail"),
    # path("account/", AccountView.as_view(), name="account"),
]
