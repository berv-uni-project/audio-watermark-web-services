from django.shortcuts import render

# Create your views here.
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Embed, Extract
from .serializers import EmbedSerializer, ExtractSerializer


class EmbedViewSet(mixins.CreateModelMixin,  
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Embed.objects.all()
    serializer_class = EmbedSerializer

class ExtractViewSet(mixins.CreateModelMixin,  
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Extract.objects.all()
    serializer_class = ExtractSerializer