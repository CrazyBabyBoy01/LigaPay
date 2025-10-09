from django.views.generic.base import TemplateView

from common.views import ContextMixin


# Create your views here.


class IndexView(ContextMixin, TemplateView):
    """
    Представление для главной страницы сайта.
    """

    template_name = 'main/index.html'
    title = 'LigaPay'
    subtitle = 'LigaPay - является гарантом на всех этапах сделки.'


class RulesView(ContextMixin, TemplateView):
    """
    Представление для страницы с правилами сервиса.
    """

    template_name = 'main/rules.html'
    title = 'Правила'
    background_color = 'brown'

    def get_context_data(self, **kwargs):
        """Добавляет переменную background_color в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['background_color'] = self.background_color
        return context
