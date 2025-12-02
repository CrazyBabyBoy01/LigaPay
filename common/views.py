class ContextMixin:
    title = 'LigaPay'
    background_image = None
    subtitle = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['background_image'] = self.background_image
        context['subtitle'] = self.subtitle
        return context
