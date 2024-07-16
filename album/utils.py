from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_drf_user_token(user):
    """
    Generate token using the Django Rest Framekwork API
    """
    token = Token.objects.create(user=user)

    return {
        'token': str(token)
    }


def user_directory_path(instance, filename):
    """
    Define the path where uploads will be saved.
    Model must include user instance.
    """
  
    file_name = filename.split('/')
    return 'images/user_{0}/{1}/{2}'.format(instance.user.id, 
                                            instance.album.id, 
                                            file_name[-1])

def resized_directory_path(instance, filename):
    """
    Define the path where resized images will be saved. 
    """
    file_name = filename.split('/')
    return 'images/user_{0}/{1}/resized/{2}'.format(instance.user.id, 
                                            instance.album.id, 
                                            file_name[-1])

def album_directory_path(instance, filename):
    """
    Define the path where uploads will be saved.
    Model must include user instance.
    """
    file_name = filename.split('/')
    return 'images/user_{0}/"album_front_img"/{1}'.format(instance.user.id, file_name[-1])
