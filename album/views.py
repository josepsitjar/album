from django.shortcuts import render

from album.models import Photo, Album
from rest_framework import viewsets
from rest_framework import permissions, generics
from album.serializers import PhotoSerializer, AlbumSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


# Create your views here.

class AlbumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows albums to be viewed or edited
    """

    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]





class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows photos to be viewed or edited.
    """

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id']
