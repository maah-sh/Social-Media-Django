from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=200, blank=True, default='')
    content = models.TextField()
    image = models.ImageField(upload_to="posts/images")
    published = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)