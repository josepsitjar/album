import datetime

from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin, User, AbstractUser
)
from django.utils import timezone
from django.dispatch import receiver

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
from djgeojson.fields import PointField, GeometryField
import os


from .utils import user_directory_path



# Create your models here.

class Album(models.Model):
    """Model for Albums"""

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

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
    #image = models.ImageField(upload_to='photos/', null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    tags = models.CharField(max_length=4000, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


# delte files on delete Photo instance
@receiver(models.signals.post_delete, sender=Photo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Delete files from filesistem
    """
    instance.image.delete()
    try:
        instance.image.delete(save=False)
    except:
        pass

class Contact(models.Model):
    """Model for contact form"""
    name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name



# User Models for app register
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
# Token django rest framework
# https://simpleisbetterthancomplex.com/tutorial/2018/11/22/how-to-implement-token-authentication-using-django-rest-framework.html
# How to user JWT token
# https://simpleisbetterthancomplex.com/tutorial/2018/12/19/how-to-use-jwt-authentication-with-django-rest-framework.html

# Authentication simple --> https://www.django-rest-framework.org/api-guide/authentication/

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    albums = models.ManyToManyField(Album, blank=True, related_name='albums_user')
