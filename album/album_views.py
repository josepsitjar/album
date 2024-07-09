from django.shortcuts import render

from django.core.mail import EmailMessage
from django.core.mail import send_mail

from album.models import Photo, Album, User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from album.serializers import PhotoSerializer, AlbumSerializer, CreateAlbumSerializer, UserSerializer,  PhotoLocalizationSerializer, ContactSerializer
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
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user, get_drf_user_token
from rest_framework.authtoken.models import Token
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.core.serializers import serialize

import subprocess
import json 
import struct

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

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user']

    
    def list(self, request, format=None):
        
        
        user = User.objects.filter(id=request.user.id)[0]
        
        """
        Staff users can view all it's own albums 
        Other users, with no permissions to access django admin, only the selected albums
        The filter by user is also done on the frontend
        """
        if user.is_staff:
            queryset = Album.objects.all()
        else: 
            queryset = user.albums.all()

        serializer_class = AlbumSerializer(queryset, many=True)
  
        return Response(serializer_class.data)

    def create(self, request, *args, **kwargs):
        """Create photo object"""
        
        serializer_class_album_creation = CreateAlbumSerializer # serializer for album creation. 

        user = request.user
        
        data = {
            "title": request.data['title'],
            "description": request.data['description'],
            "image": request.data['image'],
            "user": user.id, 
        }

        
        # For now, allow only create albums to staff members 
        if user.is_staff:
            serializer = serializer_class_album_creation(data=data, context={'user': user})
        

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, pk=None):

        user = User.objects.filter(id=request.user.id)[0]
        """
        Only staff users can delete images 
        """
        if user.is_staff:
            id = request.data['pk']
            album = Album.objects.filter(pk=id)
            album.delete()
        else:
            pass 

        return Response(status=status.HTTP_204_NO_CONTENT)
        
# resize image --> https://djangoguide.com/django-image-upload-specialization/image-upload-and-resize-django-rest-framework/
class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows photos to be viewed or edited.
    """
   
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]


    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user', 'album', 'querytext']
    
    def list(self, request, format=None):

        user = User.objects.filter(id=request.user.id)[0]

        """
        Staff users can view all it's own albums 
        Other users, with no permissions to access django admin, only the selected albums
        The filter by user is also done on the frontend
        """
        if user.is_staff:
            albums = Album.objects.all()
        else:
            albums = user.albums.all()
        
        # filter content 
        filter_text = request.query_params['querytext']

        if request.query_params['album'] == 'all':
            
            if request.query_params['querytext'] == 'null':
                queryset = Photo.objects.filter(user = user).order_by('-created_date').exclude(image__exact='')
            if request.query_params['querytext'] != 'null':
                queryset = Photo.objects.filter(Q(user = user, album__description__icontains=filter_text) 
                                                | Q(user = user, description__icontains=filter_text) 
                                                ).order_by('-created_date').exclude(image__exact='')
            
        else:
            print('query second option')
            queryset = Photo.objects.filter(album__id = request.query_params['album']).order_by('-created_date').exclude(image__exact='')
            

        serializer_class = PhotoSerializer(queryset, many=True)
  
        return Response(serializer_class.data)

    def create(self, request, *args, **kwargs):
        """Create photo object"""
        print('creating')
        permission_to_upload = self.evaluateUserSize(request)
              
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
            "thumbnail": img_field,
            #"resized_image": img_field,
            #"image": 'https://www.unigis.es/wp-content/uploads/2019/05/home5.jpg',
            "user": user.id, 
        }

        if permission_to_upload:
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
            
        else:
            return Response('NOT')
            

    def destroy(self, request, pk=None):

        user = User.objects.filter(id=request.user.id)[0]
        """
        Only staff users can delete images 
        """
        if user.is_staff:
            id = request.data['pk']
            image = Photo.objects.filter(pk=id)
            image.delete()
        else:
            pass 

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def evaluateUserSize(self, request):
        """
        Function to evaluate if user has disk space 
        """
        user = User.objects.filter(id=request.user.id)[0]
 
        bashCommand = "aws s3 ls --summarize --human-readable --recursive s3://keepyourphoto/images/user_"+str(user.id)+"/ | tail -1 | awk '{print $3}' "

        output = subprocess.check_output(bashCommand, shell=True)
        
        bytes_data = output.decode('utf-8')
  
        total_size = float(bytes_data)

        if total_size > user.contracted_size:
            return False # cannot update new photos
        else:
            return True # allowed to update new photos 

        

class PhotoSingleViewset(viewsets.ViewSet):
    """
    API endpoint that allows single photo to be viewed or edited.
    """

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user', 'album']

    def list(self, request, format=None):

        user = User.objects.filter(id=request.user.id)[0]
        photo_id = request.query_params['photo_id']
        print(photo_id)
        queryset = Photo.objects.filter(pk = photo_id)

        serializer_class = PhotoSerializer(queryset, many=True)
        return Response(serializer_class.data)

class PhotoLocalizationViewSet(viewsets.ViewSet):

    queryset = Photo.objects.exclude(geom__isnull = True).exclude(geom__exact='')
    serializer_class = PhotoLocalizationSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user']

    def list(self, request):
        #queryset_location = Photo.objects.filter(user=request.user).exclude(geom__isnull = True)
        #queryset_location = Photo.objects.filter(Q(user = request.user, geom__isnull=False)).exclude(geom__exact='')
        #serializer_class = PhotoLocalizationSerializer(queryset_location, many=True)
       
        data_list = []
        for photo in Photo.objects.exclude(geom = 'null').filter(user=request.user):
            json = {
              "type": "Feature",
              "properties": {
                'photo': str(photo.image),
                'description': photo.description,
                'album': str(photo.album),
                'photo_pk': photo.pk
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
*   Views for user info     *
*                           *
*****************************
"""


class UserInfo(viewsets.ViewSet):
    """ Views for user """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user', 'album', 'paid']
    
    def list(self, request):
        """ List user info """

        user = request.user
        #queryset = User.objects.filter(pk = request.user.pk)
        queryset = User.objects.all()
        serializer_class = UserSerializer(queryset)

        return Response(serializer_class.data)
        



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
