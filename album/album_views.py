from django.shortcuts import render

from album.models import Photo, Album
from rest_framework import viewsets
from rest_framework import permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from album.serializers import PhotoSerializer, AlbumSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
#from rest_framework import filters

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user, get_drf_user_token
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, PasswordChangeSerializer, LoginSerializer

# Create your views here.

"""
**************************
*                        *
*   Vies for album       *
*                        *
**************************
"""


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
    #permission_classes = [IsAuthenticated]
    #authentication_classes = [SessionAuthentication, BasicAuthentication]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'user']
    #search_fields = ['user']

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)




"""
**************************
*                        *
*   Views for user aut   *
*                        *
**************************
"""


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
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
