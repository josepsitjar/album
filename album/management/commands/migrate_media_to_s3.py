from django.core.management.base import BaseCommand
from django.conf import settings

import logging
import os
import boto3
from botocore.exceptions import ClientError
from django.core.files.images import ImageFile

from album.models import Photo, Album

class Command(BaseCommand):
    """
    Migrate files to s3 
    """
    
    def handle(self, *args, **options):
        # create session to s3
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            
        )

        for photo in Photo.objects.filter(album__title='album_s3'):
            image = str(photo.image)
            
            image_url = os.path.join('/home/josep/PERSONAL/album/uploads/', image)
            print(image_url)
            img_field = ImageFile(open(image_url, "rb"))
            print(img_field)
            
            photo.image.delete(save=True)
            photo.image = img_field
            photo.save()
            
    
