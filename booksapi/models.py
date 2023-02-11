from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    date_time_added = models.DateTimeField(default=timezone.now)
    book_location = models.CharField(max_length=50)
    isfav = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    book_color = models.CharField(max_length=50)
    slug = models.SlugField(max_length=250,blank=True)

    def __str__(self):
        return self.name
