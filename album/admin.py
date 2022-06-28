from django.contrib import admin

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms

from leaflet.admin import LeafletGeoAdmin

from .models import Album, Photo, Person, User
from .forms import UserCreationForm, UserChangeForm

# Admin for user registrations

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'birth_date', 'bio')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'groups', 'is_active', 'is_staff')}),
        ('Personal info', {'fields': ('birth_date', 'bio')}),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'birth_date', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Register your models here.
admin.site.register(Album)
admin.site.register(Person)
admin.site.register(Photo, LeafletGeoAdmin)
admin.site.register(User, UserAdmin)
