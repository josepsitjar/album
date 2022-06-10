from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from . import views

from album.views import PhotoViewSet

router = routers.DefaultRouter()
router.register(r'photos', views.PhotoViewSet)
#router.register(r'photos/(?P<photo_pk>\d+)', views.PhotoViewSet)
router.register(r'albums', views.AlbumViewSet)




# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_album'))
]
