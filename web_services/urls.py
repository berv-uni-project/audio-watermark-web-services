from django.conf.urls import url, include  
from rest_framework import routers
from . import views

router = routers.DefaultRouter()  
# register job endpoint in the router
router.register(r'extract', views.ExtractViewSet)
router.register(r'embed', views.EmbedViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [  
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]