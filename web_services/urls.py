from django.urls import include, re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
# register job endpoint in the router
router.register(r'extract', views.ExtractViewSet)
router.register(r'embed', views.EmbedViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    re_path(r'^(?P<version>(v1)/)', include(router.urls)),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
