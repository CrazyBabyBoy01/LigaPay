from django.db import models
from django.urls import reverse


class News(models.Model):
    """
    Модель новости с сайта League of Legends.
    """

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    url = models.URLField(unique=True, verbose_name='URL источника')
    published_at = models.DateTimeField(verbose_name='Дата публикации (Riot)')
    image = models.URLField(blank=True, null=True, verbose_name='Изображение')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено в базу')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено в базе')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        """Возвращает строковое представление новости (заголовок)."""
        return self.title

    def get_absolute_url(self):
        """Возвращает ссылку на детальную страницу новости."""
        return reverse('news_detail', kwargs={'pk': self.pk})

    def short_description(self):
        """Возвращает первые 100 символов описания."""
        return (self.description[:100] + '...') if len(self.description) > 100 else self.description

    short_description.short_description = 'Краткое описание'
