from django.shortcuts import render

from django.core.mail import EmailMessage
from django.core.mail import send_mail

from album.models import Photo, Album, User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from album.serializers import PhotoSerializer, AlbumSerializer, PhotoLocalizationSerializer, ContactSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.renderers import JSONRenderer
import os
import shutil
import io
from django.conf import settings
from .utils import user_directory_path
#from rest_framework import filters

from rest_framework_gis.filters import InBBoxFilter

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user, get_drf_user_token
from rest_framework.authtoken.models import Token
from django.core.files.storage import FileSystemStorage



from .serializers import RegistrationSerializer, PasswordChangeSerializer, LoginSerializer


# Pillow 
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import numpy as np
import pillow_heif
import cv2
import pi_heif
from pillow_heif import register_heif_opener
# Exif
#from exif import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.images import ImageFile


# Create your views here.

"""
***************************
*                         *
*   Views for album       *
*                         *
***************************
"""


class AlbumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows albums to be viewed or edited
    """

    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]
    #permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user']

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)



class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows photos to be viewed or edited.
    """
    # https://ilovedjango.com/django/rest-api-framework/views/tips/sub/modelviewset-django-rest-framework/

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    #authentication_classes = [SessionAuthentication, BasicAuthentication]


    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user', 'album']
    #search_fields = ['user']

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

    def create(self, request, *args, **kwargs):
        """Create photo object"""
              
        user = request.user
        album = Album.objects.filter(title=request.data['album'])[0]
        geom = 'null'


       
        """If image is in heic format"""
        if str(request.data['image']).split('.')[-1] == 'HEIC':

            name = '/var/www/html/files/' +str(request.data['image']).split('.')[0] + '.jpg'
            #name = str(request.data['image']).split('.')[0] + '.jpg'
            heif_file = pi_heif.open_heif(request.data['image'], convert_hdr_to_8bit=False, bgr_mode=True)
            np_array = np.asarray(heif_file)
            cv2.imwrite(name, np_array, [int(cv2.IMWRITE_PNG_COMPRESSION),9])

            img_field = ImageFile(open(name, "rb"))
            
        else:
            img_field = request.data['image']

        data = {
            "title": request.data['title'],
            "album": album.id,
            "description": request.data['description'],
            #"alb_name": request.data['album'],
            #"description": request.data['description'],
            #"created_date": request.data['created_date'],
            #"geom": request.data['geom'],
            #"geom": {'type': 'Point', 'coordinates': [0,0]},
            "geom": geom,
            #"image": request.data['image'],
            "image": img_field,
            #"image": 'https://www.unigis.es/wp-content/uploads/2019/05/home5.jpg',
            "user": user.id, 
        }

        
        
        # For now, allow only create photos to staff members 
        if user.is_staff:
            serializer = self.serializer_class(data=data, context={'user': user})
        

        if serializer.is_valid():
            serializer.save()
            if str(request.data['image']).split('.')[-1] == 'HEIC':
                os.remove(name)
                #shutil.rmtree('/var/www/html/files/')
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class PhotoLocalizationViewSet(viewsets.ViewSet):

    queryset = Photo.objects.exclude(geom__isnull = True)

    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user']

    def list(self, request):

        data_list = []
        for photo in Photo.objects.exclude(geom__isnull = True).filter(user=request.user):

            json = {
              "type": "Feature",
              "properties": {
                'photo': str(photo.image),
                'description': photo.description,
                'album': str(photo.album)
              },
              "geometry": photo.geom,
            }
            data_list.append(json)

        featureCollection = {
          "type": "FeatureCollection",
          "features": data_list
        }
        return Response(featureCollection, status=status.HTTP_200_OK)


    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)



"""
*****************************
*                           *
*   Views for contact usr   *
*                           *
*****************************
"""

class ContactViewSet(APIView):
    """ View for user contact"""

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # send email form data
            email_sender = request.data['email']
            content = request.data['message']

            send_mail(
                'Email from picbox',
                content,
                email_sender,
                ['josepsitjar@gmail.com'],
                fail_silently=False,
            )


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



"""
**************************
*                        *
*   Views for user aut   *
*                        *
**************************
"""


class RegistrationView(APIView):
    """ View for user registration """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """ View for user login """

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.loginData(request)
            username = serializer['username'].value
            password = serializer['password'].value

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                #auth_djr_token = get_drf_user_token(user)
                #auth_data = get_tokens_for_user(request.user)
                token, created = Token.objects.get_or_create(user=user)
                auth_data = {
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                }
                return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
