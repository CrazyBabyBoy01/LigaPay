from django.urls import path

from main.views import IndexView, RulesView


app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('rules/', RulesView.as_view(), name='rules'),
]
