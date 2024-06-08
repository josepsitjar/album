from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from . import album_views
from rest_framework_simplejwt import views as jwt_views
from rest_framework.authtoken import views


from album.album_views import PhotoViewSet, PhotoSingleViewset, RegistrationView, LoginView, ContactViewSet, UserInfo

router = routers.DefaultRouter()
router.register(r'photos', album_views.PhotoViewSet)
router.register(r'single_photo', album_views.PhotoSingleViewset)
router.register(r'albums', album_views.AlbumViewSet)
router.register(r'photosGeojson', album_views.PhotoLocalizationViewSet) # photos geojson feature collection
router.register(r'userinfo', album_views.UserInfo)






# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_album')),
    # djoser
    path('auth/v1/', include('djoser.urls')),
    path('auth/v1/', include('djoser.urls.authtoken')),
    # my user api
    path('accounts/register', RegistrationView.as_view(), name='register'),
    path('accounts/login', LoginView.as_view(), name='register'),
    path('accounts/contact', ContactViewSet.as_view(), name='contact'),
    # jwt token
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    # auth django rest rest_framework
    path('api-token-auth/', views.obtain_auth_token),
]
