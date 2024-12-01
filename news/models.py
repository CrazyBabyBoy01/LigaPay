from email.mime import image

from django.db import models
from django.urls import path


# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(unique=True)
    date = models.DateField()
    image = models.URLField(blank=True, null=True)

    # class Meta:
    #     verbose_name = "новость"
    #     verbose_name_plural = "новости"

    # def __str__(self):
    #     return self.title
