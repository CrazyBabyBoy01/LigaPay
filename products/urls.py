from django.urls import path

from products.views import (
    AccountServiceDetailView,
    AccountServiceListView,
    BattlePassServiceDetailsView,
    BattlePassServiceListView,
    BoostServiceDetailsView,
    BoostServiceListView,
    CategoryView,
    DonationServiceDetailsView,
    DonationServiceListView,
    GeneralServiceDetailsView,
    GeneralServiceListView,
    MyProductsView,
    OtherServiceDetailsView,
    OtherServiceListView,
    QualificationServiceDetailsView,
    QualificationServiceListView,
    RPServiceDetailView,
    RPServiceListView,
    TrainingServiceDetailsView,
    TrainingServiceListView,
)


app_name = 'products'

urlpatterns = [
    path('category/<slug:category_slug>/', CategoryView.as_view(), name='category'),
    path('accounts/', AccountServiceListView.as_view(), name='account'),
    path('riot-points/', RPServiceListView.as_view(), name='riot-points'),
    path('riot-points/<int:pk>/', RPServiceDetailView.as_view(), name='riot-points_detail'),
    path('accounts/<int:pk>/', AccountServiceDetailView.as_view(), name='accounts_detail'),
    path('boost/<int:pk>/', BoostServiceDetailsView.as_view(), name='boost_detail'),
    path('training/<int:pk>/', TrainingServiceDetailsView.as_view(), name='training_detail'),
    path('boost/', BoostServiceListView.as_view(), name='boost'),
    path('training/', TrainingServiceListView.as_view(), name='training'),
    path('battlepass/', BattlePassServiceListView.as_view(), name='battlepass'),
    path('battlepass/<int:pk>/', BattlePassServiceDetailsView.as_view(), name='battlepass_detail'),
    path('donation/', DonationServiceListView.as_view(), name='donation'),
    path('donation/<int:pk>/', DonationServiceDetailsView.as_view(), name='donation_detail'),
    path('services/', GeneralServiceListView.as_view(), name='services'),
    path('services/<int:pk>/', GeneralServiceDetailsView.as_view(), name='services_detail'),
    path('other/', OtherServiceListView.as_view(), name='other'),
    path('other/<int:pk>/', OtherServiceDetailsView.as_view(), name='other_detail'),
    path('qualification/', QualificationServiceListView.as_view(), name='qualification'),
    path(
        'qualification/<int:pk>/', QualificationServiceDetailsView.as_view(), name='qualification_detail'
    ),
    path('my-products/', MyProductsView.as_view(), name='my_products'),
]
