from django.db import models


# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(unique=True)
    date = models.DateField()
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
