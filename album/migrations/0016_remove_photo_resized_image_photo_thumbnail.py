# Generated by Django 4.2 on 2024-07-09 13:56

import album.utils
from django.db import migrations
import django_advance_thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0015_photo_resized_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='resized_image',
        ),
        migrations.AddField(
            model_name='photo',
            name='thumbnail',
            field=django_advance_thumbnail.fields.AdvanceThumbnailField(blank=True, null=True, upload_to=album.utils.resized_directory_path),
        ),
    ]
