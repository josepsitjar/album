from django.db import models
from django.utils import timezone
from django.conf import settings
from djgeojson.fields import PointField

# Create your models here.

class Album(models.Model):
    """Model for Albums"""

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Person(models.Model):
    """Model for Persons in photo"""

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Photo(models.Model):
    """Model for photos"""

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    geom = PointField(null=True, blank=True)
    album = models.ForeignKey(Album, related_name='photos', on_delete=models.SET_NULL, null=True, blank=True)
    persons = models.ManyToManyField(Person, blank=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.title
