from common.views import ContextMixin
from django.views.generic import ListView

from news.models import News


# Create your views here.


class NewsView(ContextMixin, ListView):
    model = News
    template_name = "news/news.html"
    title = "Новости"
    context_object_name = "news"
    paginate_by = 6
    ordering = ("-date",)
    background_image = "/static/deps/images/SB_Riven.jpg"
