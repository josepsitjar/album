from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Album, Photo, Person

# Register your models here.

admin.site.register(Album)
admin.site.register(Person)
admin.site.register(Photo, LeafletGeoAdmin)
