from album.models import Photo, Person, Album, User, Contact
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .utils import get_tokens_for_user, get_drf_user_token
from rest_framework.response import  Response
from rest_framework import permissions, generics, status

from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.contrib.gis.geos import Point

from PIL import Image


class AlbumSerializer(serializers.ModelSerializer):
    """Class to serialize albums"""

    photos = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['title', 'description', 'photos', 'user', 'image', 'pk']


class PhotoSerializer(serializers.ModelSerializer):
    """class to serialize photo"""

    def save(self):
        """Create Photo object"""
        
        photo = Photo(title = self.validated_data['title'],
                      user = User.objects.filter(id=self.validated_data['user'].id)[0],
                      image = self.validated_data['image'], 
                      geom = self.validated_data['geom'],
                      #album = Album.objects.filter(title=self.validated_data['album'])[0]
                      album = self.validated_data['album']
                      )
        # Check if image has exif 
        exif = Image.open(self.validated_data['image'])._getexif()
        if exif is not None:
            try:
                for key, value in exif.items():
                    if key == 34853:
                        x_decimal = float(value[2][0]) + float(value[2][1])/60 + float(value[2][2])/(60*60)
                        if value[1] == 'S':
                            x_decimal * -1
                        y_decimal = float(value[4][0]) + float(value[4][1])/60 + float(value[4][2])/(60*60)
                        if value[3] == 'W':
                            y_decimal * -1
                        geom = {'type': 'Point', 'coordinates': [y_decimal,x_decimal]} 
                        photo.geom = geom
            except:
                pass
        
        photo.save()
        
        return photo

    class Meta:
        model = Photo
        fields = ['title', 'description', 'created_date', 'geom', 'image', 'user', 'album']


class PhotoLocalizationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    #geom = GeometrySerializerMethodField


    class Meta:
        model = Photo
        geo_field = 'geom'

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('image', 'user')


class ContactSerializer(serializers.ModelSerializer):
    """Class to serialize contact"""

    def save(self):
        contact = Contact(name=self.validated_data['name'],
                          email=self.validated_data['email'],
                          message=self.validated_data['message'],
                          address=self.validated_data['address']
                          )

        contact.save()
        return contact

    class Meta:
        model = Contact
        fields = ['name', 'email', 'address', 'message']


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
