
from django.views.generic.base import TemplateView

from common.views import ContextMixin


# Create your views here.


class IndexView(ContextMixin, TemplateView):
    template_name = 'main/index.html'
    title = 'LigaPay'
    subtitle = 'LigaPay - является гарантом на всех этапах сделки.'


class RulesView(ContextMixin, TemplateView):
    template_name = 'main/rules.html'
    title = 'Правила'
    background_color = 'brown'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем переменную background_color в контекст
        context['background_color'] = self.background_color
        return context
