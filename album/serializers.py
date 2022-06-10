from album.models import Photo, Person, Album
from rest_framework import serializers


class AlbumSerializer(serializers.ModelSerializer):
    """Class to serialize albums"""

    photos = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['title', 'description', 'photos']


class PhotoSerializer(serializers.ModelSerializer):
    """class to serialize photo"""

    class Meta:
        model = Photo
        fields = ['title', 'description', 'created_date', 'geom']
