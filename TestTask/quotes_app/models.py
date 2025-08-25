from django.db import models
from django.contrib.auth.models import User


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Quote(models.Model):
    text = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('text', 'source')

    def __str__(self):
        return f"{self.text[:50]}..."


class LikeDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    value = models.IntegerField()
