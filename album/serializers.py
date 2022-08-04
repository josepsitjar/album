from album.models import Photo, Person, Album, User
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .utils import get_tokens_for_user, get_drf_user_token
from rest_framework.response import  Response
from rest_framework import permissions, generics, status

from rest_framework_gis.serializers import GeoFeatureModelSerializer



class AlbumSerializer(serializers.ModelSerializer):
    """Class to serialize albums"""

    photos = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['title', 'description', 'photos', 'user', 'image', 'pk']


class PhotoSerializer(serializers.ModelSerializer):
    """class to serialize photo"""

    class Meta:
        model = Photo
        fields = ['title', 'description', 'created_date', 'geom', 'image', 'user', 'album']


class PhotoLocalizationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Photo
        geo_field = "geom"

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('title', 'description', 'created_date', 'image', 'user', 'album')


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'birth_date', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(email=self.validated_data['email'], username=self.validated_data['email'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()

        get_drf_user_token(user)

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def loginData(self, request):
        username = self.validated_data['username']
        password = self.validated_data['password']



class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value
